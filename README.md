# How to run

1.  Find an Pexel API key [here](https://www.pexels.com/).
2.  Create an `.env` file and put the API key to the `PEXELS_API_KEY` variable:
    ```
    PEXELS_API_KEY=<your_api_key>
    ```
3.  Modify the `config.yaml` file
4.  Run
    ```
    bash scripts/run.sh
    ```
    There will be a short video that tells a short story saved in your `output_folder` that you specified on `config.yaml`. Default is `./output`.