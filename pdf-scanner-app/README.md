# PDF Scanner App

## Overview
The PDF Scanner App is a TypeScript-based application designed to scan PDF files and render their contents, including both text and images. This application provides a simple interface to extract and display data from PDF documents.

## Features
- Scans PDF files to extract text and images.
- Renders extracted text and images to the user interface.
- Built with TypeScript for type safety and maintainability.

## Project Structure
```
pdf-scanner-app
├── src
│   ├── index.ts          # Entry point of the application
│   ├── pdf
│   │   ├── scanner.ts    # Contains the Scanner class for PDF scanning
│   │   └── renderer.ts    # Contains the Renderer class for displaying content
│   └── types
│       └── index.ts      # Defines the data structures for PDF data and images
├── package.json          # NPM configuration file
├── tsconfig.json         # TypeScript configuration file
└── README.md             # Project documentation
```

## Installation
To install the necessary dependencies, run the following command:

```
npm install
```

## Usage
To start the application, run:

```
npm start
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.