import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";
import * as gcp from "@pulumi/gcp";
import * as dotenv from "dotenv";

dotenv.config();

// Obtener configuración
const config = new pulumi.Config("gcp");
const project = config.require("project");
const region = config.get("region") || "us-central1";

// Obtener variables de entorno desde la configuración de Pulumi
const apifyToken = process.env.APIFY_API_TOKEN;
const backendUrl = process.env.BACKEND_URL;

// Configuración del registro (usando GCR en este ejemplo)
const registryInfo = {
  server: "gcr.io",
  username: "_json_key",
  // La contraseña es la clave JSON en formato string
  password: process.env.GCP_SERVICE_ACCOUNT_KEY,
};

// Construir y subir la imagen del Frontend
const frontendImage = new docker.Image("frontendImage", {
  build: {
    context: "../frontend",
  },
  imageName: pulumi.interpolate`gcr.io/${project}/frontend:latest`,
  registry: registryInfo,
});

// Crear servicio de Cloud Run para el Frontend usando la imagen construida
const frontendService = new gcp.cloudrun.Service("frontendService", {
  location: region,
  template: {
    spec: {
      containers: [
        {
          image: frontendImage.imageName,
          ports: [{ containerPort: 8501 }],
          envs: [
            {
              name: "BACKEND_URL",
              value: backendUrl,
            },
            {
              name: "APIFY_API_TOKEN",
              value: apifyToken,
            },
          ],
        },
      ],
    },
  },
});

// Permitir acceso público al Frontend
const frontendIam = new gcp.cloudrun.IamMember("frontendIam", {
  service: frontendService.name,
  location: frontendService.location,
  role: "roles/run.invoker",
  member: "allUsers",
});

// Exportar las URLs de los servicios
export const frontendServiceUrl = frontendService.statuses.apply(
  (statuses) => statuses?.[0]?.url
);
