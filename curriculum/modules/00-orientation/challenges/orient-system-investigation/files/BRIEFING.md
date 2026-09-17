# EchoRelay Incident

EchoRelay should answer PING on localhost and include a lab flag in the reply.

Symptoms:
- verify fails
- connection refused
- permission denied reading the token
- wrong listen port

Fix the running system so `./echorelay/verify.sh` passes.
Do not rewrite verify.sh — make the service match the contract.
