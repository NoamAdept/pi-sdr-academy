# Troubleshooting (offline)

## `academy: command not found`

```bash
source /opt/academy/academy.env || source ~/academy/academy.env
# or:
export PYTHONPATH=/opt/academy/platform
python3 -m academy list
```

## Challenge workspace missing files

Re-run `academy start <id>` (it restages a clean copy).

## Permission denied reading a challenge file

Often intentional (Module 0 Permissions / System Investigation). Use `ls -l` and `chmod u+r` when you own the file.

## Beacon / EchoRelay will not start

1. `./service/beaconctl.sh logs` or `./echorelay/relayctl.sh logs`
2. Compare config to `.example`
3. Confirm loopback bind and existing data/dropbox paths
4. Confirm port with `ss -lntp`

## GNU Radio missing

The offline bundle must include GNU Radio `.deb`s before Module 13. Re-run developer `prepare_offline_bundle.sh` on an arm64 bookworm builder and re-install — do **not** `apt install` from the network on the student Pi.

## Verification failed

```bash
bash /opt/academy/scripts/verify_environment.sh
```

Fix FAIL lines before student handoff.
