import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// Si ya tienes Chromium/Chrome instalado (p. ej. en servidores sin internet a Google),
// indica su ruta con la variable REMOTION_BROWSER. Si no, Remotion descarga el suyo.
if (process.env.REMOTION_BROWSER) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
}
