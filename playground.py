"""Replay a few tool calls without a model or an API key."""

import argparse
import json
from dataclasses import dataclass


MAILBOXES = {"sam@example.com": {"used_gb": 47, "limit_gb": 50}}
ARTICLES = {
    "mailbox storage": "Sort mail by size and review large attachments. Empty Deleted Items after checking what's there.",
    "email delivery": "Check the recipient address and read the bounce message before retrying.",
}


class ToolError(Exception):
    pass


def get_mailbox_quota(email):
    if email == "offline@example.com":
        raise ToolError("The demo mailbox service is unavailable.")
    if email not in MAILBOXES:
        raise ToolError("No sample mailbox was found for that address.")
    return {"email": email, **MAILBOXES[email]}


def search_help_articles(query):
    query = query.casefold()
    return {
        "matches": [
            {"title": title, "guidance": guidance}
            for title, guidance in ARTICLES.items()
            if query in title
        ]
    }


# Each entry lists the one required argument and the function the app can call.
TOOLS = {
    "get_mailbox_quota": ("email", get_mailbox_quota),
    "search_help_articles": ("query", search_help_articles),
}


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: str


def execute(call):
    if call.name not in TOOLS:
        return {"error": "unknown_tool", "message": f"Tool '{call.name}' is unavailable."}

    argument, tool = TOOLS[call.name]
    try:
        args = json.loads(call.arguments)
    except json.JSONDecodeError:
        return {"error": "invalid_arguments", "message": "Arguments must be valid JSON."}

    if not isinstance(args, dict) or set(args) != {argument}:
        return {"error": "invalid_arguments", "message": f"Expected only '{argument}'."}

    value = args[argument]
    if not isinstance(value, str) or not value.strip():
        return {"error": "invalid_arguments", "message": f"'{argument}' must be a non-empty string."}

    try:
        return {"result": tool(value.strip())}
    except ToolError as exc:
        return {"error": "tool_failed", "message": str(exc)}


QUOTA = ToolCall("call_1", "get_mailbox_quota", '{"email": "sam@example.com"}')
SEARCH = ToolCall("call_2", "search_help_articles", '{"query": "mailbox storage"}')

# These saved replies stand in for the model so each case is easy to reproduce.
SCENARIOS = {
    "direct": ("What is a mail attachment?", []),
    "quota": ("How much space is left in Sam's mailbox?", [QUOTA]),
    "two-tools": ("Check Sam's storage and tell me what to do.", [QUOTA, SEARCH]),
    "bad-arguments": (
        "Check my mailbox.", [ToolCall("call_1", "get_mailbox_quota", "{}")]
    ),
    "tool-failure": (
        "Check the offline mailbox.",
        [ToolCall("call_1", "get_mailbox_quota", '{"email": "offline@example.com"}')],
    ),
}


def summarize(call, reply):
    if "error" in reply:
        return reply["message"]
    result = reply["result"]
    if call.name == "get_mailbox_quota":
        used, limit = result["used_gb"], result["limit_gb"]
        return f"{result['email']} uses {used} of {limit} GB. {limit - used} GB is free."
    if call.name != "search_help_articles":
        return json.dumps(result)
    matches = result["matches"]
    if not matches:
        return "No matching help articles."
    return "\n".join(f"{article['title']}: {article['guidance']}" for article in matches)


def replay(scenario):
    question, calls = SCENARIOS[scenario]
    print(f"User: {question}")
    if not calls:
        print("Simulated model: An attachment is a file sent with an email.")
        return

    answers = []
    for call in calls:
        print(f"Simulated model [{call.call_id}]: {call.name} {call.arguments}")
        reply = execute(call)
        print(f"Tool reply [{call.call_id}]: {json.dumps(reply)}")
        answers.append(summarize(call, reply))
    print("\nApp reply")
    print("\n".join(answers))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", choices=SCENARIOS, default="two-tools")
    replay(parser.parse_args().scenario)


if __name__ == "__main__":
    main()
