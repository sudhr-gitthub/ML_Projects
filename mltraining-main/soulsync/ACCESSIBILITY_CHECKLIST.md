# ♿ SoulSync Accessibility Checklist (WCAG AA)

This checklist targets student-friendly readability and WCAG AA alignment.

---

## 1) Color Contrast (WCAG AA)
- [ ] Normal text contrast ratio ≥ **4.5:1**
- [ ] Large text (≥ 18pt or ≥ 14pt bold) contrast ratio ≥ **3:1**
- [ ] UI components (borders, icons used as controls) contrast ratio ≥ **3:1**

### Tools
- [ ] Verify contrast using a contrast checker (e.g., WebAIM Contrast Checker).

---

## 2) Typography & Readability (Student-friendly)
- [ ] Friendly font (Poppins or Nunito)
- [ ] Clear headings and short sentences
- [ ] Avoid jargon; use simple language
- [ ] Adequate line-height (1.4–1.6)

---

## 3) Keyboard Navigation
- [ ] Everything usable with keyboard: Tab / Shift+Tab
- [ ] Buttons and inputs have clear labels
- [ ] No action requires a mouse-only gesture

---

## 4) Focus & Interaction Clarity
- [ ] Visible focus indicators
- [ ] Error messages explain “what happened” and “how to fix”
- [ ] Confirm destructive actions (delete memory/account)

---

## 5) Forms & Inputs
- [ ] Inputs have descriptive labels (not only placeholders)
- [ ] Provide hints using `st.caption()` for complex inputs
- [ ] Avoid color-only meaning (use icons + text)

---

## 6) Images & Icons
- [ ] Images include alt/caption text where possible
- [ ] Emojis/icons are supported by text labels (e.g., “📚 Study”)

---

## 7) Motion & Animations
- [ ] Avoid rapid flashing
- [ ] Optional animations (balloons) are non-essential and not frequent

---

## 8) Safety Messaging (Age Appropriate)
- [ ] Your Voice includes non-clinical disclaimer
- [ ] Crisis resources visible when harmful content is detected
- [ ] Moderation blocks sexual content and harmful instructions

---

## Quick Manual Test Script (5 minutes)
1. Use Tab to move through Dashboard and Missions.
2. Complete a mission → verify success text is readable and not color-only.
3. Open Your Voice → send a normal message → check bubble readability and disclaimer.
4. Try a toxic phrase → verify it’s flagged and safe message appears.
5. Download export JSON → ensure file downloads and includes required data.
