#!/usr/bin/env python3
"""Write the answers to synthtwin's questions as a person writes them.

Plan P4-D483 (lane WIN of the December plan). The Windows rehearsal (the
workflow file windows-bundle.yml in the repository's workflow folder)
answers the questions `synthtwin profile` put about the invented tables
the way the how-to tells a person to, then describes the table again
with `--answers`, round after round until nothing is open (an answer can
bring a new question: a column of five-figure codes answered `code` is
then asked whether its values could be ZIP codes). Each column is given
its answers in order of preference, and each open question takes the
first one it offers:

    python tools/bundle/fill_answers.py json QUESTIONS COLUMN=ANSWER[,ANSWER]...
    python tools/bundle/fill_answers.py text ANSWERS QUESTIONS COLUMN=ANSWER[,ANSWER]...
    python tools/bundle/fill_answers.py settled QUESTIONS COLUMN=ANSWER[,ANSWER]...

`json` writes each answer beside `your_answer` in the questions file
itself, as a person does in a text editor; `text` writes the plain-text
answers file, one `column = answer` line for each open question, ended
as Windows Notepad ends them (synthtwin reads it once its plain-text
route is on the line). Both refuse an open question none of whose
offered answers the column was given, so the rehearsal notices a
question it was not written for. The checklist is left as it is: a
blank there keeps the reading synthtwin chose, which is what the how-to
tells a person. `settled` reads the questions file the last run wrote
and exits 0 only when no question is open and every answer written is
kept among `answered_before`. Standard library only; it opens no
network connection.
"""

import json
import pathlib
import sys

# The sections of a questions file that hold questions a person must answer.
OPEN_SECTIONS = ("about_your_file", "about_your_table", "asked")


def preferences(words: "list[str]") -> "dict[str, tuple[str, ...]]":
    """COLUMN=ANSWER[,ANSWER...] words, read as each column's answers in order of preference."""
    found: "dict[str, tuple[str, ...]]" = {}
    for word in words:
        column, mark, answers = word.partition("=")
        chosen = tuple(answer.strip() for answer in answers.split(",") if answer.strip())
        if not mark or not column.strip() or not chosen:
            raise ValueError(f"{word!r} is not COLUMN=ANSWER[,ANSWER...]")
        found[column.strip()] = chosen
    if not found:
        raise ValueError("give at least one COLUMN=ANSWER")
    return found


def open_questions(document: "dict[str, object]") -> "list[dict[str, object]]":
    """Every question a person must answer that has no answer yet."""
    found: "list[dict[str, object]]" = []
    for section in OPEN_SECTIONS:
        listed = document.get(section)
        if isinstance(listed, list):
            found += [
                entry for entry in listed
                if isinstance(entry, dict) and not str(entry.get("your_answer") or "")
            ]
    return found


def _offered(entry: "dict[str, object]") -> "list[str]":
    choices = entry.get("answers_you_can_give")
    if not isinstance(choices, list):
        return []
    return [str(choice.get("answer")) for choice in choices if isinstance(choice, dict)]


def choose(
    document: "dict[str, object]", answers: "dict[str, tuple[str, ...]]"
) -> "tuple[list[tuple[str, str]], list[str]]":
    """(column, answer) for every open question, written into ``document``, and the problems."""
    chosen: "list[tuple[str, str]]" = []
    problems: "list[str]" = []
    for entry in open_questions(document):
        column = str(entry.get("column"))
        offered = _offered(entry)
        fitting = [answer for answer in answers.get(column, ()) if answer in offered]
        if not fitting:
            problems += [
                f"the question about {column!r} offers {', '.join(offered) or 'nothing'}, "
                f"and the rehearsal gives it {', '.join(answers.get(column, ())) or 'no answer'}"
            ]
            continue
        entry["your_answer"] = fitting[0]
        chosen += [(column, fitting[0])]
    return chosen, problems


def settled(document: "dict[str, object]", written: "list[tuple[str, str]]") -> "list[str]":
    """What, in the questions file the last run wrote, is not settled."""
    problems = [
        f"the question about {entry.get('column')!r} is still open" for entry in open_questions(document)
    ]
    before = document.get("answered_before")
    kept = {
        (str(entry.get("column")), str(entry.get("your_answer")))
        for entry in (before if isinstance(before, list) else [])
        if isinstance(entry, dict)
    }
    problems += [
        f"the answer {answer!r} about {column!r} is not kept among answered_before"
        for column, answer in written
        if (column, answer) not in kept
    ]
    return problems


def load(path: pathlib.Path) -> "dict[str, object]":
    loaded = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path.name} is not a questions file")
    return loaded


def write_json(path: pathlib.Path, document: "dict[str, object]") -> None:
    path.write_bytes((json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def write_plain(path: pathlib.Path, chosen: "list[tuple[str, str]]") -> None:
    """The plain-text answers file: one `column = answer` line each, ended as Notepad ends them."""
    path.write_bytes("".join(f"{column} = {answer}\r\n" for column, answer in chosen).encode("utf-8"))


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    route = arguments[0] if arguments else ""
    least = 4 if route == "text" else 3
    if route not in ("json", "text", "settled") or len(arguments) < least:
        print(__doc__.split("\n\n")[1])
        return 2
    try:
        answers = preferences(arguments[least - 1 :])
        questions = pathlib.Path(arguments[2] if route == "text" else arguments[1])
        document = load(questions)
        if route == "settled":
            written = [(column, given[0]) for column, given in answers.items()]
            problems = settled(document, written)
        else:
            chosen, problems = choose(document, answers)
    except (OSError, ValueError) as error:
        print(f"fill_answers: {error}")
        return 1
    if problems:
        print("fill_answers: " + "; ".join(problems))
        return 1
    if route == "json":
        write_json(questions, document)
        print(f"wrote {len(chosen)} answers into {questions.name}")
    elif route == "text":
        write_plain(pathlib.Path(arguments[1]), chosen)
        print(f"wrote {len(chosen)} answers to {pathlib.Path(arguments[1]).name}")
    else:
        print(f"{questions.name}: nothing is open and every answer is kept")
    return 0


if __name__ == "__main__":
    sys.exit(main())
