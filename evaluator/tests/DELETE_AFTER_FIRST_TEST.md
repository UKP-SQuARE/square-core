Please delete this file after you have created the first file. This file ensures we can commit the directory `tests`. Otherwise, the docker container fails while building:

```
Step 15/19 : COPY tests tests
1 error occurred:
    * Status: COPY failed: file not found in build context or excluded by .dockerignore: stat tests: file does not exist, Code: 1
```