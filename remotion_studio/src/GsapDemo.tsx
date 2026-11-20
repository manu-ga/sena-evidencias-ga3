import { useLayoutEffect, useRef } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import gsap from "gsap";

/**
 * GSAP dentro de Remotion: la línea de tiempo se crea en pausa y se posiciona
 * en el segundo exacto de cada fotograma, así el render es determinista.
 */
export const GsapDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const raiz = useRef<HTMLDivElement>(null);
  const tl = useRef<gsap.core.Timeline | null>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      const t = gsap.timeline({ paused: true });
      t.from(".caja", { y: 300, opacity: 0, scale: 0.4, rotation: -25, duration: 0.8, ease: "back.out(1.7)", stagger: 0.15 })
        .to(".caja", { rotation: 360, duration: 1.2, ease: "power2.inOut", stagger: 0.1 }, 1.1)
        .to(".titulo", { letterSpacing: "0.08em", duration: 1.6, ease: "sine.inOut" }, 0.4);
      tl.current = t;
    }, raiz);
    return () => ctx.revert();
  }, []);

  useLayoutEffect(() => {
    tl.current?.seek(frame / fps, false);
  }, [frame, fps]);

  const colores = ["#ff7a3d", "#ffd23f", "#3aa76d", "#4aa3ff"];
  return (
    <AbsoluteFill ref={raiz} style={{ background: "#1b0f2e", alignItems: "center", justifyContent: "center", fontFamily: "sans-serif" }}>
      <div className="titulo" style={{ color: "white", fontSize: 100, fontWeight: 800, marginBottom: 120 }}>GSAP + Remotion</div>
      <div style={{ display: "flex", gap: 40 }}>
        {colores.map((c) => (
          <div key={c} className="caja" style={{ width: 200, height: 200, borderRadius: 36, background: c }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
