import sys
from datetime import datetime, timezone

from src.notification import tracer_decision, valider_action
from src.workflow import traiter_log, traiter_pipeline, traiter_scan

LOGS = [
    "2026-10-05 10:00:01 INFO backend Service demarre",
    "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123",
    "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123",
    "2026-10-05 10:03:20 ERROR backend OOMKilled restarts=15",
    "2026-10-05 10:04:30 ERROR backend OOMKilled restarts=16",
    "2026-10-05 10:05:40 ERROR backend OOMKilled restarts=17",
]
RAPPORTS_PIPELINE = [
    {"job": "build", "status": "failed", "date": "2026-10-05T10:06:00Z"},
]
RAPPORTS_SCAN = [
    {"cve": "CVE-2026-1234", "package": "lib-xyz", "severity": "critical",
     "date": "2026-10-05T10:07:00Z"},
]


def afficher(resultat, audit):
    notif, ana = resultat["notification"], resultat["analyse"]
    print(f"--- {notif.event_id} -> {notif.channel} ({notif.recipient})")
    print(notif.text)
    if ana.sensitive:
        reponse = input("Action sensible. Approuver ? (o/n) : ")
        ok = valider_action(ana, reponse)
        maintenant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        tracer_decision(ana, ok, "ops-oncall", audit, maintenant)
        print("Action", "APPROUVEE" if ok else "REFUSEE",
              "(simulation : rien n'est execute)")
    print()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    vus, compteur, historique, audit = set(), {}, [], []
    entrees = [(traiter_log, x) for x in LOGS]
    entrees += [(traiter_pipeline, x) for x in RAPPORTS_PIPELINE]
    entrees += [(traiter_scan, x) for x in RAPPORTS_SCAN]
    ignores = 0
    for numero, (traiter, brut) in enumerate(entrees, start=1):
        resultat = traiter(brut, numero, vus, compteur, historique)
        if resultat is None:
            ignores += 1
            print(f"--- EVT-{numero:05d} ignore (doublon)\n")
        else:
            afficher(resultat, audit)
    print(f"{len(entrees)} evenements recus, {ignores} doublon(s) ignore(s), "
          f"{len(historique)} notification(s), {len(audit)} decision(s) tracee(s).")


if __name__ == "__main__":
    main()
