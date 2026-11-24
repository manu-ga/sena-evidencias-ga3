import React from "react";

/** Banderas dibujadas en SVG (versiones simplificadas, proporción 3:2). */
export type Team = "ARG" | "BRA" | "URU" | "CHI" | "COL" | "PAR" | "PER";

export const TEAM_NAME: Record<Team, string> = {
  ARG: "ARGENTINA", BRA: "BRASIL", URU: "URUGUAY", CHI: "CHILE", COL: "COLOMBIA", PAR: "PARAGUAY", PER: "PERÚ",
};
export const TEAM_COLOR: Record<Team, string> = {
  ARG: "#75AADB", BRA: "#FFDF00", URU: "#4A90D9", CHI: "#D52B1E", COL: "#FCD116", PAR: "#D52B1E", PER: "#D91023",
};

const Sun: React.FC<{ cx: number; cy: number; r: number }> = ({ cx, cy, r }) => (
  <g>
    {Array.from({ length: 16 }, (_, i) => {
      const a = (i * Math.PI * 2) / 16;
      return <line key={i} x1={cx + Math.cos(a) * r * 0.9} y1={cy + Math.sin(a) * r * 0.9} x2={cx + Math.cos(a) * r * 1.6} y2={cy + Math.sin(a) * r * 1.6} stroke="#F6B40E" strokeWidth={r * 0.22} strokeLinecap="round" />;
    })}
    <circle cx={cx} cy={cy} r={r} fill="#F6B40E" stroke="#85340A" strokeWidth={r * 0.08} />
  </g>
);

const Star: React.FC<{ cx: number; cy: number; r: number }> = ({ cx, cy, r }) => {
  const pts = Array.from({ length: 10 }, (_, i) => {
    const a = -Math.PI / 2 + (i * Math.PI) / 5;
    const rr = i % 2 === 0 ? r : r * 0.4;
    return `${cx + Math.cos(a) * rr},${cy + Math.sin(a) * rr}`;
  }).join(" ");
  return <polygon points={pts} fill="#FFFFFF" />;
};

const FlagArt: React.FC<{ team: Team }> = ({ team }) => {
  switch (team) {
    case "ARG":
      return (<g><rect width="300" height="200" fill="#75AADB" /><rect y="66.7" width="300" height="66.7" fill="#FFF" /><Sun cx={150} cy={100} r={17} /></g>);
    case "BRA":
      return (<g><rect width="300" height="200" fill="#009C3B" /><polygon points="150,22 278,100 150,178 22,100" fill="#FFDF00" />
        <circle cx="150" cy="100" r="46" fill="#002776" /><path d="M106,92 Q150,80 194,108" stroke="#FFF" strokeWidth="9" fill="none" /></g>);
    case "URU":
      return (<g><rect width="300" height="200" fill="#FFF" />
        {[1, 3, 5, 7].map((k) => <rect key={k} y={(200 / 9) * k} width="300" height={200 / 9} fill="#0038A8" />)}
        <rect width="120" height={(200 / 9) * 5} fill="#FFF" /><Sun cx={60} cy={55} r={17} /></g>);
    case "CHI":
      return (<g><rect width="300" height="200" fill="#FFF" /><rect y="100" width="300" height="100" fill="#D52B1E" />
        <rect width="100" height="100" fill="#0039A6" /><Star cx={50} cy={50} r={26} /></g>);
    case "COL":
      return (<g><rect width="300" height="100" fill="#FCD116" /><rect y="100" width="300" height="50" fill="#003893" /><rect y="150" width="300" height="50" fill="#CE1126" /></g>);
    case "PAR":
      return (<g><rect width="300" height="66.7" fill="#D52B1E" /><rect y="66.7" width="300" height="66.7" fill="#FFF" /><rect y="133.3" width="300" height="66.7" fill="#0038A8" />
        <circle cx="150" cy="100" r="25" fill="#FFF" stroke="#0038A8" strokeWidth="3" /><circle cx="150" cy="100" r="17" fill="none" stroke="#2E7D32" strokeWidth="3" />
        <polygon points="150,91 153,98 161,98 155,103 157,110 150,106 143,110 145,103 139,98 147,98" fill="#F6B40E" /></g>);
    case "PER":
      return (<g><rect width="300" height="200" fill="#FFF" /><rect width="100" height="200" fill="#D91023" /><rect x="200" width="100" height="200" fill="#D91023" /></g>);
  }
};

/** Bandera con ondeo sutil (sombra que recorre la tela) y borde. */
export const Flag: React.FC<{ team: Team; width: number; frame?: number; radius?: number; glow?: boolean }> = ({ team, width, frame = 0, radius = 14, glow = false }) => {
  const h = (width * 2) / 3;
  const sheen = ((frame * 2.2) % 420) - 120;
  const id = `fl-${team}-${width}`;
  return (
    <svg width={width} height={h} viewBox="0 0 300 200" style={{ borderRadius: radius, boxShadow: glow ? `0 0 60px ${TEAM_COLOR[team]}88, 0 18px 40px rgba(0,0,0,.6)` : "0 18px 40px rgba(0,0,0,.55)", display: "block" }}>
      <defs>
        <linearGradient id={id} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#000" stopOpacity="0" />
          <stop offset="0.5" stopColor="#000" stopOpacity="0.22" />
          <stop offset="1" stopColor="#000" stopOpacity="0" />
        </linearGradient>
        <clipPath id={`${id}-c`}><rect width="300" height="200" rx={radius * (300 / width)} /></clipPath>
      </defs>
      <g clipPath={`url(#${id}-c)`}>
        <FlagArt team={team} />
        <rect x={sheen} y="0" width="110" height="200" fill={`url(#${id})`} />
        <rect width="300" height="200" fill="none" stroke="rgba(255,255,255,.35)" strokeWidth="4" />
      </g>
    </svg>
  );
};
