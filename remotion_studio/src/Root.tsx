import { Composition } from "remotion";
import { Demo } from "./Demo";
import { GsapDemo } from "./GsapDemo";

// Vertical 9:16 (1080x1920) a 24 fps, igual que el resto del proyecto.
export const Root: React.FC = () => (
  <>
  <Composition
    id="Demo"
    component={Demo}
    durationInFrames={72}
    fps={24}
    width={1080}
    height={1920}
    defaultProps={{ titulo: "Remotion listo", subtitulo: "Animal Factory" }}
  />
  <Composition id="GsapDemo" component={GsapDemo} durationInFrames={96} fps={24} width={1080} height={1920} />
  </>
);
