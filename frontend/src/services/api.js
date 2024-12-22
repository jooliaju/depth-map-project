const API_BASE_URL = "http://127.0.0.1:5000/api";

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await fetch(`${API_BASE_URL}/upload-image`, {
      method: "POST",
      body: formData,
      headers: {},
      mode: "cors",
      credentials: "include",
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
  imageName,
  annotations,
  withScribbles
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/save-annotations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        imageName,
        annotations,
        withScribbles,
      }),
      mode: "cors",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
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

export const processFocus = async (imageName, focusPoint, options = {}) => {
  const response = await fetch(`${API_BASE_URL}/process-focus`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      imageName,
      focusPoint,
      ...options,
    }),
  });
  return response.json();
};
