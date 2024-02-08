## Diese Repository enthält das von uns im Umfang unserer Seminararbeit verwendete Datenbereinigungsprogramm.

Die Zweige (*Branches*) sind wie folgt aufgebaut:

| Zweig  | Beschreibung                 |
| :---------  | :------------------- |
| `legacy` | Die von uns verwendete, nicht korrekt funktionierende Version des Programms   |
| `legacy-corrected` | Eine abgeänderte Version des Programmes, die minimale Änderungen zu `legacy` enthält um die Fehler in der Funktionalität zu beseitigen   |
| `main` | Die aufgeräumte und reparierte Variante des Programms   |

Zum Ausführen des Programmes wird `python3` benötigt.

Eine beispielhafte Ausführung sieht wie folgt aus:

```python3
python3 ./parser.py "/home/user/ai3_2024-01-0104:09:39.333951/castlingBonus" "/home/user/output_directory_for_csv_files" 0.1 0.25 0.33 0.45
```

Die Parameter haben folgende Bedeutung:

| Parameter | Bedeutung |
| ---- | ---- |
| `"/home/user/ai3_2024-01-0104:09:39.333951/castlingBonus"` | Der zu verarbeitende Datensatz. |
| `"/home/user/output_directory_for_csv_files"` | Verzeichnis in dem die CSV-Dateien abgelegt werden sollen |
| `0.1` | Verwendete Gewichtung für `WeightBishopPos` (wird als String in die erste Zeile der CSV geschrieben, hat anderweitig keinen Einfluss) |
| `0.25` | Verwendete Gewichtung für `WeightRooksPos` (wird als String in die erste Zeile der CSV geschrieben, hat anderweitig keinen Einfluss) |
| `0.33` | Verwendete Gewichtung für `WeightQueenPos` (wird als String in die erste Zeile der CSV geschrieben, hat anderweitig keinen Einfluss) |
| `0.45` | Verwendete Gewichtung für `WeightCastlingBonus` (wird als String in die erste Zeile der CSV geschrieben, hat anderweitig keinen Einfluss) |
