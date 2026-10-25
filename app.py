import streamlit as st
from PIL import Image
from io import BytesIO
from privacy_scanner import scan_text, redact_text
from image_analyzer import scan_image, redact_image

st.set_page_config(page_title="Digital Footprint Guardian", page_icon="🛡️", layout="wide")

st.title("🛡️ Digital Footprint Guardian")
st.write("Scan text or screenshots for potentially sensitive information before sharing them.")
st.caption("Privacy-first demo: processing happens in this app session. Avoid testing with real passwords or confidential documents.")

tab_text, tab_image = st.tabs(["📝 Scan text", "🖼️ Scan screenshot"])

with tab_text:
    st.subheader("Text privacy scanner")
    text = st.text_area(
        "Paste text to check",
        height=180,
        placeholder="Example: Contact me at student@example.com or 9876543210"
    )
    if st.button("Scan text", type="primary", key="scan_text"):
        if not text.strip():
            st.warning("Enter some text first.")
        else:
            result = scan_text(text)
            st.session_state["text_scan_result"] = result
            st.session_state["original_text"] = text

    if "text_scan_result" in st.session_state:
        result = st.session_state["text_scan_result"]
        st.metric("Privacy risk score", f'{result["score"]}/100', result["level"])
        st.progress(result["score"] / 100)

        if result["score"] >= 70:
            st.error("🔴 High Risk: Review and protect sensitive information before sharing.")
        elif result["score"] >= 30:
            st.warning("🟠 Medium Risk: Check the detected items before sharing.")
        else:
            st.success("🟢 Low Risk: Fewer supported sensitive patterns were detected.")

        st.info("Tip: Use the protected text below instead of sharing the original.")
        if result["findings"]:
            st.write("**Detected items**")
            st.dataframe(
                [{"Type": f["type"], "Count": f["count"], "Risk": f["risk"]} for f in result["findings"]],
                use_container_width=True,
                hide_index=True
            )
            st.write("**Suggested protected text**")
            st.code(redact_text(st.session_state["original_text"]), language="text")
            st.download_button(
                "Download redacted text",
                data=redact_text(st.session_state["original_text"]),
                file_name="redacted_text.txt",
                mime="text/plain"
            )
        else:
            st.success("No supported sensitive patterns were detected. This does not guarantee the text is safe to share.")

with tab_image:
    st.subheader("Screenshot privacy scanner")
    st.write("Upload a screenshot. OCR attempts to find email addresses, phone numbers, and common secret-like strings.")
    uploaded = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)
        if st.button("Scan screenshot", type="primary"):
            with st.spinner("Reading image text..."):
                try:
                    result = scan_image(image)
                    st.session_state["image_scan_result"] = result
                    st.session_state["original_image"] = image
                except RuntimeError as e:
                    st.error(str(e))

    if "image_scan_result" in st.session_state:
        result = st.session_state["image_scan_result"]
        st.metric("Privacy risk score", f'{result["score"]}/100', result["level"])
        st.progress(result["score"] / 100)

        if result["score"] >= 70:
            st.error("🔴 High Risk: Protect sensitive information before sharing.")
        elif result["score"] >= 30:
            st.warning("🟠 Medium Risk: Review detected items before sharing.")
        else:
            st.success("🟢 Low Risk: Fewer supported sensitive patterns detected.")

        if result["findings"]:
            st.dataframe(
                [{"Type": f["type"], "Count": f["count"], "Risk": f["risk"]} for f in result["findings"]],
                use_container_width=True,
                hide_index=True
            )
            protected = redact_image(st.session_state["original_image"], result["boxes"])
            st.image(protected, caption="Protected copy — detected text areas are covered", use_container_width=True)
            buffer = BytesIO()
            protected.save(buffer, format="PNG")
            st.download_button(
                "Download protected image",
                data=buffer.getvalue(),
                file_name="protected_screenshot.png",
                mime="image/png"
            )
        else:
            st.info("No supported sensitive patterns were detected in OCR text. Small, blurry, or stylized text may be missed.")

st.divider()
st.caption("Limitations: pattern-based detection can produce false positives and miss sensitive information. Always review the protected output before sharing.")
