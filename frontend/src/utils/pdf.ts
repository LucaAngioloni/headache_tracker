import jsPDF from "jspdf";
import html2canvas from "html2canvas";

const BACKGROUND = "#fffdf9";

async function capture(element: HTMLElement) {
  return html2canvas(element, {
    scale: 2,
    backgroundColor: BACKGROUND,
    useCORS: true,
    logging: false,
  });
}

export async function exportSectionsToPdf(
  elements: HTMLElement[],
  filename: string,
): Promise<void> {
  const canvases = [];
  for (const el of elements) {
    canvases.push(await capture(el));
  }

  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "pt",
    format: "a4",
    compress: true,
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 24;
  const imgWidth = pageWidth - margin * 2;

  let first = true;
  for (const canvas of canvases) {
    if (!first) pdf.addPage();
    first = false;

    const img = canvas.toDataURL("image/jpeg", 0.95);
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = margin;

    pdf.addImage(img, "JPEG", margin, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft > 0) {
      position -= pageHeight;
      pdf.addPage();
      pdf.addImage(img, "JPEG", margin, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }
  }

  pdf.save(filename);
}
