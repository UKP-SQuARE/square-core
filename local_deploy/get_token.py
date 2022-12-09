"""
An example script to get the ClientCredentials token. This token is used to bypass authentication in SQuARE services.
"""

from utils import SharedVariables

if __name__ == "__main__":
    print(SharedVariables.token)
