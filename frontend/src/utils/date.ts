export function toDisplay(value: string): string {
  if (!value) return "";
  const m = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return value;
  return `${m[3]}/${m[2]}/${m[1]}`;
}

export function fromDisplay(display: string): string {
  const m = display.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (!m) return "";
  const dd = Number(m[1]);
  const mon = Number(m[2]);
  const yyyy = Number(m[3]);
  if (mon < 1 || mon > 12 || dd < 1 || dd > 31 || yyyy < 1) return "";
  const mm = String(mon).padStart(2, "0");
  const day = String(dd).padStart(2, "0");
  return `${yyyy}-${mm}-${day}`;
}
