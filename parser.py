"""
Version 3.0

In der dritten Version des Parsers fällt die Score-Berechnung weg. Der Parser nimmt eine PGN-Datei als Eingabe
entgegen, löscht alle nicht für die Analyse notwendigen Daten aus der Datei raus und schreibt die restlichen
Daten in eine CSV-Datei.

Diese Iteration passierte als Folge davon, dass der ursprünglich berechnete Score keinen Nutzen in der Analyse fand.


Version 2.0

In der zweiten Version des Parsers werden die Parameter des Bots direkt aus dem
Header der PGN-Dateien ausgelesen. Außerdem sind die Gewichtungen der einzelnen
Parameter jetzt durch Daniil bereitgestellt und in die Berechnung mit einbezogen.

Weiter werden nun sowohl der Score des weißen als auch des schwarzen spielers
berechnet, weil nun beide Spieler der Bot sind.

Vorher war immer nur ein Spieler der Bot, daher gab es nur einen Score.


Version 1.0

In der ersten Version des Parsers ist die Grundlegende Funktionalität sichergestellt.
Es wird ein Score berechnet, indem die ELO-Anzahl des Gegners des Schach-Bots durch die
Anzahl der Züge des Spiels geteilt wird.

"""
import re

"""
Example Usage:

user@local:~/ai3_datasets/ai3_2023-12-3122:45:50.208778$ ls
rookPos/

user@local:~/ai3_datasets/ai3_2023-12-3122:45:50.208778$ python3 ~/parser.py rookPos/ ~/temp 1 1 1 1

"""

import chess.pgn
import os
import csv
import sys

"""
In diesem Array steht die Gewichtung der einzelnen Parameter.
Die einzelnen Parameter kommen direkt von Daniil und stehen genauso im Bot.
"""

weightsMap = dict(
    playername="",          # Nothing, This is the Name of the Bot
    search_Depth=4,         # Search Depth
    weight_PawnPos=1,       # WeightPawnPos
    biaSpawnPosPieceCount=16,   # BiasPawnPosPieceCount
    weightKnightsPos=1.3,       # WeightKnightsPos
    weightBishopPos=sys.argv[3],    # WeightBishopPos
    weightRooksPos=sys.argv[4],     # WeightRooksPos
    weightQueenPos=sys.argv[5],     # WeightQueenPos
    weightCastlingBonus=sys.argv[6] # WeightCastlingBonus
)

"""
Gibt PGN-Objekt einer Datei zurück
"""


def getChessGameObject(pgn_filename):
    # File pgn_file = new File("")
    pgn_file = open(pgn_filename)

    return chess.pgn.read_game(pgn_file)


"""
Gibt den Header Eines PGN-Objekts zurück.

Bekommt aber entweder 'white' oder 'black' als
zusätzlichen parameter. Liest also nur die Parameter
des schwarzen od. weißen spielers.
"""


def getHeader(chess_game, color):
    checkColor(color)  # throws exception for wrong color param

    if color.lower() == "white":
        return chess_game.headers["White"]
    elif color.lower() == "black":
        return chess_game.headers["Black"]


"""
Überprüft ob die übergebene Farbe (string) entweder "black" oder "white" ist.

Diese Methode wird in der getHeader() methode verwendet um den übergebenen Parameter auf
Validität zu prüfen.
"""


def checkColor(color):
    if color.lower() not in ["black", "white"]:
        raise Exception("Invalid Header Parameter - Need 'White' or 'Black'")


"""
Erhält als Eingabe das Resultat des Spiels (1-0, 0-0 oder 0-1) als string
und gibt das konvertierte Resultat als float (1, 0.5 oder 0) aus sicht des jeweiligen
Spielers zurück.

Bei einem Unentschieden wird '0.5', '0.5' zurückgegeben.


--- Beispiel ---

Resultat '1-0' beschreibt, dass weiß gewonnen und schwarz verloren hat.
Damit gibt diese Methode die werte '1' und '0' zurück.
"""


def resultModifier(r):
    rw = r[0]  # res white
    rb = r[1]  # res black

    if rw > rb:
        rw = 1
        rb = 0
    elif rw < rb:
        rw = 0
        rb = 1
    else:
        rw = 0.5
        rb = 0.5

    return str(rw), str(rb)


"""
Diese Methode gibt den Score eines Spielers zurück.

Jeweils entsprechend der resultModifier()-Methode wird entweder 0, 0.5 oder 1 zurückgegeben.
"""


def getResult(chess_game, color):
    checkColor(color)
    rw, rb = resultModifier(chess_game.headers["Result"].split("-"))

    if color.lower() == "white":
        return rw
    elif color.lower() == "black":
        return rb


"""
Diese Methode ist für das Beschreiben der CSV-Dateien zuständig.
Sie ersetzt die alte write()-Methode, die sich unten findet (write_old()).

Sie nimmt alle Parameter als Eingabe entgegen und schreibt diese als eine einzige Reihe
in die Datei.

Um die gesamte Datei zu beschreiben wird diese Methode in einer Schleife in main() aufgerufen.
"""


def write(gameCount, file, header, isWinner):
    parameters = list(header.split("||"))

    parameters[0] += f"_{gameCount+1}"
    parameters.append(isWinner)

    with open(file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        writer.writerow(parameters)


"""
Diese Methode gibt true oder false zurück, je nachdem ob ein übergebener Dateipfad eine leere
Datei ist.

Dies wurde benutzt um sicherzustellen dass die CSV-Dateien richtig inizialisiert worden sind.
"""


def isEmpty(path):
    with open(path, 'r') as p:
        content = p.readlines()
    #print(f"Content of {path}: {content} -- {content == []}")
    return content == []


"""
Diese Methode erstellt eine neue CSV-Datei. Sie wird vor der write()-Methode aufgerufen
um die notwendige Datei zu erstellen und die erste Zeile mit den Bezeichnungen und Gewichtungen
in die Datei zu schreiben.
"""


def initializeFile(filename):
    os.system(f"install -Dv /dev/null {filename}")

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        newarray = list(weightsMap.keys()) + ["isWinner"]
        weights = list(weightsMap.values()) + [1]

        for i in enumerate(newarray):
            newarray[i[0]] = i[1] + f"({weights[i[0]]})"

        writer.writerow(newarray)


"""
Diese Methode ist für das Aufrufen und Steuern des Vorgangs zuständig.

Sie ersetzt die alte main()-Methode, die sich unten findet (main_old()).
"""


def main():
    """
    In jedem Unterverzeichnis sind die Parameter des Bots leicht anders. (s. Daniils Nachricht in Discord)

    Wir berechnen also für jedes Unterverzeichnis einen Score, den plottet Dennis und das analysieren wir
    dann in der Arbeit.
    """

    global iteration
    print("Writing, Please Wait", end="... ")

    directory = sys.argv[1]  # Oberstes Verzeichnis
    csvdir = sys.argv[2]

    # Unterverzeichnis 1,2,3,4,...,7
    for subdirectory in os.listdir(directory):

        # Jede iteration (iterblack/iterwhite) im Unterverzeichnis 1,2,3,...7
        iterations = os.listdir(os.path.join(directory, subdirectory))
        iterations.sort(key=natural_keys)

        for iteration in iterations:
            counter = 0

            csv_file_path = f"{csvdir}/{iteration}_{subdirectory}"
            csv_file_path_black = f"{csv_file_path}_black.csv"
            csv_file_path_white = f"{csv_file_path}_white.csv"

            initializeFile(csv_file_path_black)
            initializeFile(csv_file_path_white)


            pgn_files = os.listdir(f"{directory}/{subdirectory}/{iteration}")
            pgn_files.sort(key=natural_keys)

            # Jeder File in der Iteration
            for file in pgn_files:
                pgn_file_path = f"{directory}/{subdirectory}/{iteration}/{file}"
                if os.path.isfile(pgn_file_path) and not isEmpty(pgn_file_path):
                    print("Processing: ", pgn_file_path)
                    write(counter,
                          csv_file_path_black,
                          getHeader(getChessGameObject(pgn_file_path), "Black"),
                          getResult(getChessGameObject(pgn_file_path), "Black")
                          )
                    write(counter,
                          csv_file_path_white,
                          getHeader(getChessGameObject(pgn_file_path), "White"),
                          getResult(getChessGameObject(pgn_file_path), "White")
                          )

                    counter += 1

    print("Done")



def atoi(text):
    return int(text) if text.isdigit() else text

"""
Dieser Schlüssel sorgt für das richtige Sortieren der rohen Datensätze
"""
def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


# Starte das Programm durch
# Aufruf der Main-Methode
main()




"""
Ab hier folgen Methoden, die keine Verwendung in der aktuellen Version finden. 
"""

"""
Diese Methode ist für das Aufrufen und Steuern des Vorgangs zuständig.

Diese Methode wird NICHT mehr verwendet.
"""


def main_old():
    """
    In jedem Unterverzeichnis sind die Parameter des Bots leicht anders. (s. Daniils Nachricht in Discord)

    Wir berechnen also für jedes Unterverzeichnis einen Score, den plottet Dennis und das analysieren wir
    dann in der Arbeit.
    """

    global iteration
    print("Writing, Please Wait", end="... ")

    scoresBlack = []
    resultsBlack = []
    scoresWhite = []
    resultsWhite = []

    directory = sys.argv[1]  # Oberstes Verzeichnis
    csvdir = sys.argv[2]

    # Unterverzeichnis 1,2,3,4,...,7
    for subdirectory in os.listdir(directory):

        # Jede iteration (iterblack/iterwhite) im Unterverzeichnis 1,2,3,...7
        for iteration in os.listdir(f"{directory}/{subdirectory}"):

            # Jeder File in der Iteration
            for file in os.listdir(f"{directory}/{subdirectory}/{iteration}"):
                path = f"{directory}/{subdirectory}/{iteration}/{file}"
                if os.path.isfile(path) and not isEmpty(path):
                    score_white, score_black, result_white, result_black = process(path)

                    scoresWhite.append(score_white)
                    scoresBlack.append(score_black)

                    resultsWhite.append(result_white)
                    resultsBlack.append(result_black)

        # Average Score von Schwarz
        avg_res_black = 0
        avg_black = 0
        avg_res_white = 0
        avg_white = 0

        for i in enumerate(scoresBlack):
            avg_black += float(i[1])
        avg_black = avg_black / len(scoresBlack)

        for i in enumerate(scoresWhite):
            avg_white += float(i[1])
        avg_white = avg_white / len(scoresWhite)

        for iteration in os.listdir(f"{directory}/{subdirectory}"):
            initializeFile(f"{csvdir}/{iteration}_{subdirectory}_csv_white.csv")
            initializeFile(f"{csvdir}/{iteration}_{subdirectory}_csv_black.csv")
            counter = 0

            # Jeder File in der Iteration
            for file in os.listdir(f"{directory}/{subdirectory}/{iteration}"):
                path = f"{directory}/{subdirectory}/{iteration}/{file}"
                if not isEmpty(path):
                    chess_game = getChessGameObject(path)

                    print(f"Importing {path}")

                    write(file.split(".")[0].replace("Game", ""), scoresWhite[counter],
                          f"{csvdir}/{iteration}_{subdirectory}_csv_white.csv",
                          getHeader(chess_game, "white"), avg_white, resultsWhite[counter])
                    write(file.split(".")[0].replace("Game", ""), scoresBlack[counter],
                          f"{csvdir}/{iteration}_{subdirectory}_csv_black.csv",
                          getHeader(chess_game, "black"), avg_black, resultsBlack[counter])

                    counter += 1

    print("Done")


"""
Diese Methode nimmt einen header als Eingabe entgegen und iteriert über alle parameter
des headers.
Die parameter werden mit der gewichtung multipliziert und aufaddiert.
Der schließliche Wert, 'score' genannt, wird zurückgegeben.

Diese Methode wird NICHT mehr verwendet.
"""


def getScore(header):
    return  # Diese Methode wird nicht mehr verwendet

    score = 0  # Score für den jeweiligen header (also spieler)

    for i in enumerate(header.split("||")):  # || ist der delimiter eines parameters

        # Der erste Parameter des Headers ist der Name des Spielers.
        # Interessiert uns nicht, ist immer der Bot.
        if i[0] == 0:
            continue

        # parameter: (1, 4.03)

        print(f"Weight: {float(list(weightsMap.values())[i[0]])}")
        print(f"Value: {float(i[1])}")

        score += float(i[1]) * float(list(weightsMap.values())[i[0]])
    #            ^^^^^^^^^^^
    #        i[1] ist der wert des headers.
    #        i[0] ist die Position (also 0, 1, 2, ...)
    #
    #           Das kommt von enumerate().

    #        Der Wert des Headers ist standardmäßig ein String.
    #        Wir casten den zu nem Float, weil wir mit nem String
    #        "4.00" nichts anfangen können

    #       Wir multiplizieren den Wert des Parameters mit dem Wert im
    #       'weights'-Array an der Stelle des Parameters
    #
    #       Der 1-te eintrag des Arrays ist gleichzeitig die Gewichtung des 1-ten
    #       Parameters, der 2-te eintrag des Arrays ist die Gewichtung des 2-ten Parameters usw.
    #       daher weights[i[0]].
    #                     ^^^^
    #               Das war die Position des Parameters

    return score  # Gib den Score zurück


"""
Diese Methode bekommt einen PGN-Datei-Pfad als Eingabeparameter
und verwendet die anderen Methoden um den Score der gesamten Datei zu berechnen.

Diese Methode wird NICHT mehr verwendet.
"""


def process(path):
    print(f"Processing {path}")

    chess_game = getChessGameObject(path)

    """
    Der Score wird wie folgt berechnet:

    Parameter des Bots (jeweils im Header der Datei) 
    multipliziert mit der Gewichtung aus dem 'weight'-array

    Die Berechnung erfolgt für Schwarz & Weiß separat. 
    Es werden zwei Scores zurückgegeben

    """

    score_white = getScore(getHeader(chess_game, "White"))  # Score des Weißen Spielers
    score_black = getScore(getHeader(chess_game, "Black"))  # Score des Schwarzen Spielers

    result_white = getResult(chess_game, "White")  # 0, 0.5 or 1
    result_black = getResult(chess_game, "Black")  # ""

    return score_white, score_black, result_white, result_black


"""
Diese Methode ist für das Beschreiben der CSV-Dateien zuständig.

Sie nimmt alle Parameter als Eingabe entgegen und schreibt diese als eine einzige Reihe
in die Datei.

Um die gesamte Datei zu beschreiben wird diese Methode in einer Schleife in main() aufgerufen.

Diese Methode wird NICHT mehr verwendet.
"""
def write_old(gameCount, score, file, header, avgScore, avgWin):
    parameters = list(header.split("||"))

    parameters[0] += f"_{gameCount}"

    parameters.append(score)
    parameters.append(avgScore)

    if str(avgWin) != str(0.5):
        avgWin = int(avgWin)

    parameters.append(avgWin)

    with open(file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        writer.writerow(parameters)
