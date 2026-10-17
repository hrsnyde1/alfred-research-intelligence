# Research line: live test runbook (owner-run)

For Hayden to run on `alfred@192.168.50.81` with sudo. Nothing here has been run on the server yet. Memory publishing stays **OFF** (owner decision 2026-10-16); this test proves the line itself. Personal Photon, Hermes and Memory are not restarted or changed.

**Never paste credentials into chat or into these docs.** Type them only at the server prompts below.

## What you need before starting

- The **Research** Photon project ID and secret (the separate Research project, not Personal).
- Your iPhone, able to text **+1 (415) 225-0168**.
- About 20 minutes, and a terminal on the server where you can run `sudo`.

## 0. Package on the Mac

```bash
cd ~/Git/alfred-research-intelligence && git switch feat/research-line && git pull --ff-only
```
```bash
git archive --prefix=research-line/ -o /tmp/research-line.tgz HEAD src scripts staging/research-photon-line-v1
```
```bash
shasum -a 256 /tmp/research-line.tgz
```
```bash
scp /tmp/research-line.tgz alfred@192.168.50.81:/home/alfred/research-line.tgz
```

## 1. Pre-checks on the server (read-only)

```bash
sha256sum ~/research-line.tgz    # must match the Mac value
systemctl is-active alfred-photon.service alfred-hermes.service alfred-memory-v1.service   # note these: all must stay as they are
systemctl is-active alfred-research-photon.service   # expect: inactive
sudo test -x /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node && echo node-ok
sudo test -d /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/node_modules/spectrum-ts && echo sdk-ok
```
Stop if any check fails, or if `alfred-research-photon` is already active.

## 2. Install (files only; nothing starts)

```bash
cd ~ && tar -xzf research-line.tgz
sudo cp -a /opt/alfred-research-photon/v1 /opt/alfred-research-photon/v1.canary-backup
sudo cp -a /etc/systemd/system/alfred-research-photon.service /root/alfred-research-photon.service.canary-backup
S=~/research-line/staging/research-photon-line-v1
sudo install -o root -g root -m 0644 $S/connector.mjs $S/research-project.mjs $S/outbox.mjs $S/main.mjs $S/discover.mjs /opt/alfred-research-photon/v1/
sudo install -o root -g root -m 0644 $S/alfred-research-photon.service $S/alfred-research-photon-discover.service $S/alfred-research-line.service /etc/systemd/system/
sudo install -d -o root -g root -m 0755 /opt/alfred-research-line/v1
sudo cp -R ~/research-line/src ~/research-line/scripts /opt/alfred-research-line/v1/
sudo chown -R root:root /opt/alfred-research-line/v1 && sudo chmod -R go-w /opt/alfred-research-line/v1
sudo install -o root -g root -m 0700 $S/line_setup.py /root/line_setup.py
sudo systemctl daemon-reload
```

## 3. Research Photon credentials (you type them; they are never displayed)

```bash
sudo install -d -o root -g root -m 0700 /etc/alfred-research-photon/credentials
sudo bash -c 'umask 077; read -r -p "Research project ID: " v; printf %s "$v" > /etc/alfred-research-photon/credentials/research-project-id'
sudo bash -c 'umask 077; read -r -s -p "Research project secret: " v; echo; printf %s "$v" > /etc/alfred-research-photon/credentials/research-project-secret'
```

## 4. Discover the line binding (2-minute window, sends nothing)

```bash
sudo python3 /root/line_setup.py challenge
```
This prints 16 digits. Have your phone ready with a new message to **+1 (415) 225-0168** containing exactly those digits. Then run the command below and **send the text right away**. The command waits up to 2 minutes and returns once it sees your message.

```bash
sudo systemctl start alfred-research-photon-discover.service; sudo journalctl -u alfred-research-photon-discover.service -n 5 --no-pager
```

Expected journal line: `{"state":"DISCOVERED"}`. To check the report:

```bash
sudo python3 -c "import json;r=json.load(open('/var/lib/alfredresearch-photon/discovery.json'));print({k:r[k] for k in ('line','shared_line','usable','space_type')})"
```

- `shared_line: False` and `usable: True` → continue.
- `shared_line: True` → **stop.** Photon is giving this project only the shared line, so Research would be mixed with Personal. Tell me, and contact Photon about a dedicated line.
- `{"state":"NO_MATCH"}` or exit 2 → the text didn't arrive, or credentials or the SDK failed. Repeat step 4; generate a new challenge, and to discard the old report run `sudo rm /var/lib/alfredresearch-photon/discovery.json` if it exists. Send me the journal lines (they contain no secrets).

## 5. Write the configs (line on, Memory publishing off)

```bash
sudo python3 /root/line_setup.py configure
```

## 6. Start both services (not enabled at boot yet)

```bash
sudo systemctl start alfred-research-photon.service && sleep 10 && sudo cat /var/lib/alfredresearch-photon/health.json; echo
sudo systemctl start alfred-research-line.service && sleep 3 && systemctl is-active alfred-research-line.service
sudo journalctl -u alfred-research-line.service -n 20 --no-pager
```
Expect health `"state":"READY"` with `"outbox":"ENABLED"`, and the worker `active`.

## 7. Phone acceptance test

Text the Research line, one message at a time, waiting for each reply:

| # | You text | Pass when you receive |
|---|---|---|
| 1 | `help` | Usage message ("Send me a link…") |
| 2 | `https://www.rfc-editor.org/rfc/rfc9110.html` | "On it: researching … (job research-…)", then within about a minute "Research complete … 4 of 4 findings source-supported …" ending with "Memory: candidate kept locally, not published to Alfred's Memory." |
| 3 | the same link again | "Already researched in the last day …" |
| 4 | `status` | "Recent research:" listing the job as completed |
| 5 | `https://youtu.be/dQw4w9WgXcQ` | "On it…", then "Research stopped: unsupported source … Nothing was inferred …" |
| 6 | `What is the history of HTTP idempotent methods?` | "On it: researching the question …", then a result or "stopped: needs sources" |

Then confirm nothing else changed:

```bash
systemctl is-active alfred-photon.service alfred-hermes.service alfred-memory-v1.service
sudo ls /var/lib/alfredresearch-photon/outbox/unknown /var/lib/alfredresearch-photon/outbox/rejected
```
The first command must match step 1. Both outbox folders should be empty. Also send Personal Alfred a normal message and confirm it replies as usual.

## 8. Tell me

Paste these (no secrets in any of them):
- the output of `discovery.json` from the check in step 4 (`line`, `shared_line`, `usable`, `space_type`);
- the health line from step 6;
- the replies you received for messages 1–6, or which number failed;
- `sudo journalctl -u alfred-research-line.service -n 50 --no-pager` and `sudo journalctl -u alfred-research-photon.service -n 20 --no-pager` if anything failed.

If everything passed, you decide whether to start the services at boot:

```bash
sudo systemctl enable alfred-research-photon.service alfred-research-line.service
```

## Rollback (any time)

```bash
sudo systemctl stop alfred-research-line.service alfred-research-photon.service
sudo cp -a /opt/alfred-research-photon/v1.canary-backup/. /opt/alfred-research-photon/v1/
sudo cp -a /root/alfred-research-photon.service.canary-backup /etc/systemd/system/alfred-research-photon.service
sudo systemctl daemon-reload
```
Research state stays in `/var/lib/alfred-research-line` and `/var/lib/alfredresearch-photon`. Credentials stay in `/etc/alfred-research-photon/credentials` until you remove them.

## Later: Memory publishing (Phase B, after a model provider is chosen)

Not part of this test. It will need: a model provider for the `alfredresearchphoton` account, a `research-line` Memory **agent** principal token at `/etc/alfred-research-line/credentials/memory-token` (provisioned by you with the Alfred Memory token, typed at a server prompt), uncommenting `LoadCredential=memory-token` in `alfred-research-line.service`, the Memory port in the config, `memory.enabled: true`, and the Memory kind decision. I'll prepare the exact commands when you pick the provider.
