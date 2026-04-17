/**
 * Optional microphone preflight for clearer permission UX before Web Speech.
 * Not all browsers expose getUserMedia; STT may still prompt on recognition.start().
 */

export async function requestMicPermissionPreview() {
  if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
    return { ok: true, mode: "no_preflight" };
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((t) => t.stop());
    return { ok: true, mode: "granted" };
  } catch (err) {
    const name = err && typeof err === "object" && "name" in err ? String(err.name) : "";
    if (name === "NotAllowedError" || name === "PermissionDeniedError") {
      return { ok: false, mode: "denied", error: err };
    }
    if (name === "NotFoundError" || name === "DevicesNotFoundError") {
      return { ok: false, mode: "no_device", error: err };
    }
    return { ok: false, mode: "unavailable", error: err };
  }
}

export function describeMicBlockReason(preview) {
  if (!preview || preview.ok) {
    return "";
  }
  if (preview.mode === "denied") {
    return "Microphone access was denied. Allow the microphone for this site in the browser address bar, or type your request.";
  }
  if (preview.mode === "no_device") {
    return "No microphone was found. Connect a microphone or type your request.";
  }
  return "Microphone could not be opened. Check browser settings or type your request.";
}
