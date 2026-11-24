export const C = {
  bg: "#0B0F17",
  ads: "#F97316",
  trading: "#06B6D4",
  white: "#FFFFFF",
  red: "#EF4444",
  panel: "#121826",
  dim: "#8B95A7",
};

export type Side = "ads" | "trading" | "red" | "white";

export const sideColor = (s?: string): string =>
  s === "ads" ? C.ads : s === "trading" ? C.trading : s === "red" ? C.red : C.white;

export const FONT = "Inter, 'Helvetica Neue', Arial, sans-serif";
export const W = 1080;
export const H = 1920;
/** Centro vertical de los subtítulos: dentro de la zona segura (lejos de los bordes de la interfaz del feed). */
export const SUB_Y = 1250;
