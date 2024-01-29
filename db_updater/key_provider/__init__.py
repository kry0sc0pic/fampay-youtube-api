class KeyProvider:
    def __init__(self, keys=None):
        if keys is None:
            import os
            KEYS = os.environ.get("KEYS", ["invalid-api-key"])
            self.keys = eval(KEYS.replace("'", '"'))
        else:
            self.keys = keys
        self.nextKey = self.keys[0]
        self.keyUsage = {key: 0 for key in self.keys}

    def _log_key_usage(self):
        for key, usage in self.keyUsage.items():
            print(f"Key {key[0:5]}..{key[10:]}: {usage} units")

    """
    Remove a key from the list of keys whose quota has been used up
    """
    def remove_key(self, key):
        """
        Invalidates a key, making it unusable
        """
        self.keyUsage.pop(key)
        self.keys.remove(key)
        self.nextKey = sorted(self.keyUsage.items(), key=lambda x: x[1])[0][0]
        if len(self.keys) == 0:
            raise ValueError("No keys left")

    """
    Returns the next key to use
    
    :param units: The number of units the request uses from quota. Default is 1
    """

    def key(self, cost=1) -> str:
        self.keyUsage[self.nextKey] += cost
        self._log_key_usage()
        key = self.nextKey
        self.nextKey = sorted(self.keyUsage.items(), key=lambda x: x[1])[0][0]
        return key
