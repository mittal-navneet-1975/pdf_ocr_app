export interface PDFData {
    text: string;
    images: ImageData[];
}

export interface ImageData {
    src: string;
    alt?: string;
}