export class Renderer {
    renderText(text: string): void {
        // Implementation for rendering text to the UI
        console.log("Rendering text:", text);
    }

    renderImages(images: ImageData[]): void {
        // Implementation for rendering images to the UI
        images.forEach(image => {
            console.log("Rendering image:", image);
        });
    }
}