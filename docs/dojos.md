# Dojos & belts

Pi SDR Academy uses a **dojo / belt** progression inspired by hands-on cyber
education platforms (notably the pedagogical model popularized by pwn.college):

- You start with a **white belt** mindset: terminal-first, offline, iterative.
- **Core Material** unlocks belts in order — finish a dojo, earn the belt, reveal the next.
- **Side Quests** are optional depth (language / GNU Radio C++ qualification).
- Challenges are educational first; keep spoilers private when used in a class.

## Core path

| Belt | Dojo | Modules |
|------|------|---------|
| White | Intro to the Lab | orientation, linux-cli |
| Yellow | Software Craft | python → git-workflow |
| Orange | Systems Core | systems-programming, computer-architecture |
| Green | DSP Foundations | dsp-fundamentals, fft, dsp-filters |
| Blue | Radio Path | iq-sdr → synchronization |
| Purple | Receivers & Radio Security | complete-receivers, protocol-re, sdr-security-ctf |
| Black | Capstone — Blackout | capstone-blackout |

## Side quests

| Belt | Dojo | Modules |
|------|------|---------|
| Brown | Language Qualification | python-qualification, cpp-qualification, gnuradio-cpp |

Defined in `curriculum/dojos.yaml`.

## Play

```bash
academy serve                 # open http://127.0.0.1:8080/
# or
academy next
cd /challenge                 # ~/challenge on a laptop
cat README.txt
./check
```
