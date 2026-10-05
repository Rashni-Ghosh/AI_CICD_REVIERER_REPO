| Component        | Technology               |
| ---------------- | ------------------------ |
| API              | FastAPI                  |
| AI               | Ollama                   |
| LLM              | Small local model        |
| CI/CD            | GitHub Actions           |
| SCM              | GitHub                   |
| Static checks    | Python/YAML/custom rules |
| Language         | Python                   |
| Deployment later | AWS                      |


Responsible for exact, deterministic issues:

hard-coded secrets
shell=True
os.system
eval
exec
Docker latest
Docker root
mutable GitHub Actions
excessive workflow permissions

"The deterministic engine catches known, rule-based security and CI/CD violations, while the AI reviewer performs semantic analysis to identify additional reliability, code-quality, configuration, and CI/CD issues. The final layer removes overlapping findings so the user doesn't receive duplicate recommendations."

ai-test.py issue:
#ISSUES TO IDENTIFY:
# | Code                                         | Possible AI observation                                                       |
# | -------------------------------------------- | ----------------------------------------------------------------------------- |
# | `requests.get(url)`                          | No timeout specified                                                          |
# | `except:`                                    | Bare exception handling                                                       |
# | `except: pass`                               | Errors are silently ignored                                                   |
# | `return total / len(numbers)`                | Potential division-by-zero                                                    |
# | `calculate_average([])`                      | Function is explicitly called with an empty list                              |
# | `"https://api.example.com/users/" + user_id` | URL construction could be improved/validated                                  |
# | `open("result.txt", "w")`                    | File handling could be improved with explicit encoding/context considerations |
