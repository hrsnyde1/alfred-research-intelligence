"""Reserved Research ingress; no ordinary-agent fallback or credential access."""
import asyncio
import hashlib
import json
import os
import weakref

PREFIX = 'photon-research:'
_issued = weakref.WeakValueDictionary()

def configuration(env=None):
    env = os.environ if env is None else env
    if env.get('PHOTON_RESEARCH_ENABLED') != '1':
        raise ValueError('Research unavailable')
    keys = ('CONNECTION_REF','LINE','SPACE','SENDER','PROFILE')
    values = {k.lower():env.get('PHOTON_RESEARCH_'+k) for k in keys}
    if any(not isinstance(v,str) or not v or v != v.strip() for v in values.values()):
        raise ValueError('Research binding unavailable')
    return values

def receive(adapter, wire, message_factory, env=None):
    c=configuration(env)
    r=wire.get('research',{})
    if (wire.get('project')!='research' or wire.get('projectBinding')!='research-connection-v1'
        or any(r.get(k)!=c[k] for k in c)
        or not isinstance(r.get('route'),str) or not r['route'].startswith(PREFIX)
        or wire.get('space',{}).get('id')!=r['route']
        or wire.get('sender',{}).get('id')!=c['sender']
        or not isinstance(wire.get('messageId'),str) or not wire['messageId'].startswith('research:')
        or not r.get('originalMessageId') or wire.get('content',{}).get('type')!='text'):
        raise ValueError('Research event denied')
    text=wire['content'].get('text')
    if not isinstance(text,str) or len(text.encode())>65536:
        raise ValueError('Research text denied')
    source=adapter.build_source(chat_id=r['route'],chat_name='Research',chat_type='dm',
        user_id=c['sender'],user_name='Research requester',message_id=wire['messageId'])
    event=message_factory(text=text,source=source,message_id=wire['messageId'],raw_message=wire)
    _issued[id(event)]=event
    return event

async def guard(runner,event):
    source=event.source
    wire=getattr(event,'raw_message',None)
    reserved=str(getattr(source,'chat_id','')).startswith(PREFIX)
    if not reserved and not (isinstance(wire,dict) and wire.get('project')=='research'):
        return False,None
    unavailable='Research intake is unavailable; no research has started.'
    try:
        if _issued.get(id(event)) is not event:
            return True,None  # forged/unknown: no outbound response
        c=configuration()
        if runner._profile_name_for_source(source)!=c['profile']:
            return True,None  # missing/incorrect profile: no dispatch
        source.profile=c['profile']
        from gateway.run_inbound_consumer import _routed_scope
        from hermes_cli.lifecycle import ainvoke_hook,has_hook
        async with _routed_scope(runner,source):
            if not has_hook('research_project_intake'):
                return True,unavailable
            results=await asyncio.wait_for(ainvoke_hook('research_project_intake',
                source=source.to_dict(),message_id=event.message_id,text=event.text,
                research_identity=dict(wire['research']),project_binding='research-connection-v1'),10)
        if len(results)!=1 or not isinstance(results[0],dict) or results[0].get('action')!='handled':
            return True,unavailable
        reply=results[0].get('reply')
        return True,reply if isinstance(reply,str) and reply.strip() else None
    except asyncio.CancelledError:
        raise
    except Exception:
        return True,unavailable if _issued.get(id(event)) is event else None

def outbound(path,body):
    result=dict(body)
    space=result.get('spaceId','')
    if str(space).startswith(PREFIX):
        configuration()
        # Narrow pending-ACK path; no Research richlink/media/typing fallback.
        if path!='/send' or result.get('format','text')!='text':
            raise ValueError('Research action unavailable')
        result['project']='research'
        if not isinstance(result.get('operationId'),str) or not result['operationId'].startswith('research:'):
            raise ValueError('authenticated originating Research operation required')
    else:
        if result.get('project') not in (None,'personal'):
            raise ValueError('cross-project outbound denied')
        result['project']='personal'
    return result
