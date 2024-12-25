import config from "../config";

const { API_BASE_URL } = config;

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await fetch(`${API_BASE_URL}/upload-image`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error("Error uploading image:", error);
    throw error;
  }
};

export const saveAnnotations = async (
  imageData,
  annotations,
  withScribbles
) => {
  try {
    console.log("Saving annotations");
    const response = await fetch(`${API_BASE_URL}/save-annotations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        imageData,
        annotations,
        withScribbles,
      }),
    });

    const data = await response.json();

    console.log("Annotations saved");
    return {
      status: "success",
      images: data.images,
    };
  } catch (error) {
    console.error("Error saving annotations:", error);
    throw error;
  }
};

export const processDepth = async (imageName, options = {}) => {
  const response = await fetch(`${API_BASE_URL}/process-depth`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      imageName,
      ...options,
    }),
  });
  return response.json();
};

export const processFocus = async (
  imageData,
  anisotropicResult,
  focusPoint,
  options = {}
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/process-focus`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        imageData,
        anisotropicResult,
        focusPoint,
        depthRange: options.depthRange || 0.1,
        kernelSizeGaus: options.kernelSizeGaus || 5,
        kernelSizeBf: options.kernelSizeBf || 5,
        sigmaColor: options.sigmaColor || 200,
        sigmaSpace: options.sigmaSpace || 200,
        gausSigma: options.gausSigma || 60,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error("Error processing focus:", error);
    throw error;
  }
};

export const processAnisotropic = async (
  imageData,
  options = {},
  onProgress
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/process-anisotropic`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        imageData,
        annotations: options.annotations,
        mask: options.mask,
        ignoreMask: options.ignoreMask,
        beta: options.beta || 0.1,
        iterations: options.iterations || 3000,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const events = decoder.decode(value).split("\n\n");
      for (const event of events) {
        if (event.trim()) {
          try {
            const data = JSON.parse(event.replace("data: ", ""));
            if (data.progress !== undefined) {
              onProgress?.(data.progress);
            } else if (data.status === "success") {
              result = data;
            } else if (data.status === "error") {
              throw new Error(data.message);
            }
          } catch (parseError) {
            console.error("Error parsing event:", parseError);
          }
        }
      }
    }

    if (!result) {
      throw new Error("No result received from server");
    }

    return result;
  } catch (error) {
    console.error("Error processing anisotropic:", error);
    throw error;
  }
};
