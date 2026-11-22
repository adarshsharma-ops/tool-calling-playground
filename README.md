# Tool-Calling Playground

A small Python example of what happens after a model asks to call a tool. The app looks up the tool, checks the arguments, and prints the result alongside the original call ID.

## Run it

From the cloned repository, run the command below with Python 3.9 or newer. It uses the standard library and sample data. Everything runs offline.

```sh
python3 playground.py
```

The default example checks a sample mailbox and finds a storage tip. The trace shows the simulated request and the actual result from each Python function.

```text
Simulated model [call_1]: get_mailbox_quota {"email": "sam@example.com"}
Tool reply [call_1]: {"result": {"email": "sam@example.com", "used_gb": 47, "limit_gb": 50}}
```

| Run | What to look for |
| --- | --- |
| `python3 playground.py direct` | The scripted answer arrives without a tool call. |
| `python3 playground.py quota` | A single call reports how much space is free. |
| `python3 playground.py two-tools` | The two replies have separate call IDs. |
| `python3 playground.py bad-arguments` | The app rejects a request that omits the email address. |
| `python3 playground.py tool-failure` | Valid arguments reach the tool, which reports a simulated outage. |

## How it works

`SCENARIOS` contains the questions and scripted model replies. `execute()` accepts only names listed in `TOOLS`, then checks the JSON and the expected argument. Each tool reads a small local fixture. `summarize()` turns the results into a final reply using plain Python. A live integration would normally send those results back to the model using the call IDs.

Try changing `sam@example.com` in `QUOTA` to a different address. The call should pass validation and fail inside the tool. Then change the JSON field from `email` to `address` and see how the error differs.

To add a tool, write a function, register its name and argument in `TOOLS`, and add a case to `SCENARIOS`. The current dispatcher expects one string argument per tool.
