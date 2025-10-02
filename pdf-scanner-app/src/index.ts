import { Scanner } from './pdf/scanner';
import { Renderer } from './pdf/renderer';

async function main() {
    const scanner = new Scanner();
    const renderer = new Renderer();

    try {
        const filePath = 'path/to/your/pdf/file.pdf'; // Update with the actual file path
        const pdfData = await scanner.scanPDF(filePath);
        const extractedText = scanner.extractText(pdfData);
        
        renderer.renderText(extractedText);
        renderer.renderImages(pdfData.images);
    } catch (error) {
        console.error('Error scanning or rendering PDF:', error);
    }
}

main();