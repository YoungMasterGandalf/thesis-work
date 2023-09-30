# Diploma Thesis Project - Kernel integrals in time--distance helioseismology

![Version](https://img.shields.io/badge/version-v1.0-blue)

<img src="https://github.com/YoungMasterGandalf/thesis-work/blob/main/sunny.png" alt="Sunny" width="100"/>

I will add some smart comment here eventually... 🤓

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ut dui eu urna ultrices consectetur. Nulla facilisi. Proin in tristique eros. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Pellentesque aliquet tristique justo. Phasellus nec vestibulum ex. Vestibulum euismod auctor quam, a commodo libero lacinia in. Vestibulum dignissim mauris a ullamcorper mollis.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ut dui eu urna ultrices consectetur. Nulla facilisi. Proin in tristique eros. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Pellentesque aliquet tristique justo. Phasellus nec vestibulum ex. Vestibulum euismod auctor quam, a commodo libero lacinia in. Vestibulum dignissim mauris a ullamcorper mollis.

## Features

- Lorem ipsum feature 1
- Lorem ipsum feature 2
- ...

## Installation

To install and run this project, follow these steps:

1. Clone this repository.
2. Navigate to the project directory.
3. Follow the steps mentioned in **Usage** chapter

## Usage

> [!WARNING]
> The code is still in a stage of development so it might be a little wild sometimes. Consider yourself warned.

> [!NOTE]
> The code is developed mainly to be run on a cluster as PBS jobs but separate tasks can be run on local machine via python as well.

The basic usage on a cluster can be described in a very simplified pipeline as follows:
`datacube_pipeline_prerequisitor.py` --> (`download_selected_queries.py`) --> `datacube_pipeline_runner.py`

1. `datacube_pipeline_prerequisitor.py` prepares the whole folder structure base on the inputs we give to it. The configuration is done at the begnning of the file via Python constants. After running the script, two helper files located at `./datacube_pipeline_helper_files/` are made/altered:
   * `datacube_maker_inputs.json` containing various directory and file paths needed for a correct run of subsequent .pbs files
   * `requests_ready_for_download.json` containing pairs of JSOC requests and the paths to folders where the data from these requests will be stored

2. If you need to download some data before running the datacube and travel-time pipelines, you have to run `download_selected_queries.py` as a middle step. This will go through the `requests_ready_for_download.json` file and download all the requests stored there into the paths mentioned as values (each request:path pair gets deleted from the file after it's download is complete without failure). If you want to run the downloads, drink your coffee ☕ and enjoy your life, try running `run_download_queries.pbs`. It will run the downloads as jobs on the cluster, so you can logout and enjoy your life.

3. Last but not least, when all your data is ready, you can run `datacube_pipeline_runner.py` which will query all the jobs (both for creating datacubes and for running traveltime calculations) on cluster.

> [!WARNING]
> When you post more datacubes you might want to change your name on the cluster to something like Fantomas so no-one knows who's running the thing. The reason is that it takes so much RAM and CPU that your colleagues might become somewhat hostile towards you pretty quickly for stalling their work. Safety first!

## Contributing

If you would like to contribute to this project, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Description of your changes'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request with a detailed description of the changes.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to customize the template further according to your specific needs. Remember to replace the placeholder text with your actual content.
