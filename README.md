# Kriptomagazin – Slack monitoring bot

Brezplačna prva različica: na približno 5 minut preveri `https://kriptomagazin.si/` in `/kripto-novice/`. Po **2 zaporednih neuspešnih preverjanjih** objavi opozorilo v Slack, ob okrevanju pa drugo obvestilo. Ne pošilja sporočil ob vsakem preverjanju.

## 1. Ustvari Slack aplikacijo in webhook

1. V Slacku ustvari kanal, npr. `#monitoring-kriptomagazin`.
2. Pojdi na https://api.slack.com/apps in izberi **Create New App → From scratch** oziroma **Blank app**.
3. Poimenuj jo `Kriptomagazin Monitor`, izberi svoj workspace, potrdi.
4. Odpri **Incoming Webhooks → Activate Incoming Webhooks**.
5. Klikni **Add New Webhook to Workspace**, izberi kanal in potrdi.
6. Kopiraj ustvarjeni `https://hooks.slack.com/services/...` URL in ga **ne objavljaj ali pošiljaj v klepet**.

## 2. Zaženi na GitHub Actions

1. Ustvari **javni** GitHub repozitorij (npr. `kriptomagazin-slack-monitor`) in vanj naloži vse datoteke, vključno s skrito `.github` mapo. Noben webhook ni v kodi.
2. V repozitoriju odpri **Settings → Secrets and variables → Actions → New repository secret**.
3. Dodaj skrivnost z imenom `SLACK_WEBHOOK_URL` in vrednostjo iz 1. koraka.
4. V **Settings → Actions → General → Workflow permissions** omogoči **Read and write permissions** za shranjevanje stanja med zagoni.
5. Odpri **Actions → Kriptomagazin Slack Monitor → Run workflow**.
6. Prvi uspešen zagon samo izpiše `OK` v GitHub Actions log. Za test opozoril začasno zamenjaj en URL v `TARGETS` v `monitor.py` z napačnim, dvakrat sproži workflow in ga nato vrni na pravilnega.

## Omejitve

- Delovanje je odvisno od GitHub Actions razporejevalnika, ki lahko zamuja/izpušča zagone. Najkrajši interval je 5 minut; to ni monitoring na sekundo.
- Scheduled workflows v javnih neaktivnih repozitorijih po 60 dneh lahko postanejo onemogočeni; redno preverjaj Actions.
- GitHub-hosted standard runner je brezplačen za **javne** repozitorije. Za zasebne repoje veljajo minute/kvote računa.
- Trenutno vidi HTTP/povezovalne napake, ne strežniških PHP logov, CPU/RAM ali root cause. Nekateri požarni zidovi lahko blokirajo GitHub runnerje, zato preveri lažne alarme.
- Bot **ne bere Slack sporočil in ne sprejema ukazov**. Za `/status` ali AI analizo bi bilo treba izdelati interaktivnega Slack bota.
