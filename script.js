// Get live location
document.getElementById("getLocationBtn").addEventListener("click", () => {
  if ("geolocation" in navigator) {
    document.getElementById("getLocationBtn").disabled = true;
    document.getElementById("getLocationBtn").textContent = "Getting location...";
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const locationText = `Latitude: ${lat.toFixed(6)}, Longitude: ${lng.toFixed(6)}`;
        document.getElementById("locationInput").value = locationText;
        document.getElementById("getLocationBtn").disabled = false;
        document.getElementById("getLocationBtn").textContent = "Get Live Location";
      },
      (error) => {
        alert("Error getting location: " + error.message);
        document.getElementById("getLocationBtn").disabled = false;
        document.getElementById("getLocationBtn").textContent = "Get Live Location";
      }
    );
  } else {
    alert("Geolocation not supported by your browser");
  }
});

// Image compression function
function compressImage(base64Image, maxWidth = 800, quality = 0.7) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      let width = img.width;
      let height = img.height;
      
      // Resize if needed
      if (width > maxWidth) {
        height = (maxWidth / width) * height;
        width = maxWidth;
      }
      
      canvas.width = width;
      canvas.height = height;
      
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, width, height);
      
      // Compress to JPEG with quality setting
      const compressedImage = canvas.toDataURL("image/jpeg", quality);
      resolve(compressedImage);
    };
    img.src = base64Image;
  });
}

// Feedback submission function
async function submitFeedback(reportId) {
  const selectedFeedback = document.querySelector(`input[name="feedback-level-${reportId}"]:checked`);
  const feedbackText = document.getElementById(`feedback-text-${reportId}`).value;
  const statusSpan = document.getElementById(`feedback-status-${reportId}`);
  
  if (!selectedFeedback) {
    statusSpan.textContent = "⚠️ Please select a feedback option";
    statusSpan.style.color = "#ff6b6b";
    return;
  }
  
  try {
    statusSpan.textContent = "📤 Submitting feedback...";
    
    const response = await fetch("/submit-feedback", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        report_id: reportId,
        feedback_type: selectedFeedback.value,
        feedback_comment: feedbackText
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      statusSpan.textContent = "✅ Feedback received! Thank you for helping improve the AI.";
      statusSpan.style.color = "#28a745";
      
      // Disable feedback form after submission
      document.querySelectorAll(`input[name="feedback-level-${reportId}"]`).forEach(input => {
        input.disabled = true;
      });
      document.getElementById(`feedback-text-${reportId}`).disabled = true;
    } else {
      statusSpan.textContent = "❌ Error submitting feedback: " + data.message;
      statusSpan.style.color = "#dc3545";
    }
  } catch (error) {
    statusSpan.textContent = "⚠️ Failed to submit feedback";
    statusSpan.style.color = "#ff6b6b";
    console.error("Feedback error:", error);
  }
}

function displayRiskAssessment(assessment, imageBase64, reportId) {
  if (!assessment) return "";
  
  const riskColor = {
    1: "#28a745", // Green
    2: "#5cb85c", // Light green
    3: "#ffc107", // Yellow
    4: "#fd7e14", // Orange
    5: "#dc3545"  // Red
  };
  
  const color = riskColor[assessment.risk_level] || "#ffc107";
  
  let html = `
    <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-left: 5px solid ${color}; border-radius: 4px;">
      <h3 style="margin-top: 0; color: ${color};">🤖 AI Risk Assessment (Gemini)</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- Image Section -->
        <div style="display: flex; flex-direction: column; align-items: center;">
          ${imageBase64 ? `<img src="${imageBase64}" style="max-width: 100%; max-height: 300px; border-radius: 8px; border: 2px solid ${color};" alt="Uploaded damage image">` : ''}
          <p style="font-size: 12px; color: #666; margin-top: 10px;">Uploaded Image</p>
        </div>
        
        <!-- Assessment Section -->
        <div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
            <div>
              <p style="margin: 5px 0;"><strong>Risk Level:</strong></p>
              <p style="font-size: 24px; color: ${color}; margin: 5px 0;">${assessment.risk_level}/5 ●</p>
            </div>
            <div>
              <p style="margin: 5px 0;"><strong>Safety Risk:</strong></p>
              <p style="font-size: 24px; color: ${color}; margin: 5px 0;">${assessment.safety_risk || assessment.risk_level}/5 ●</p>
            </div>
          </div>
          <p><strong>Urgency:</strong> <span style="background: ${color}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">${(assessment.urgency || "medium").toUpperCase()}</span></p>
  `;
  
  if (assessment.damage_type) {
    html += `<p><strong>Damage Type:</strong> ${assessment.damage_type}</p>`;
  }
  
  if (assessment.identified_risks && assessment.identified_risks.length > 0) {
    html += `<p><strong>Identified Risks:</strong></p><ul style="margin: 5px 0; padding-left: 20px;">`;
    assessment.identified_risks.forEach(risk => {
      html += `<li>${risk}</li>`;
    });
    html += `</ul>`;
  }
  
  if (assessment.recommended_actions && assessment.recommended_actions.length > 0) {
    html += `<p><strong>Recommended Actions:</strong></p><ul style="margin: 5px 0; padding-left: 20px;">`;
    assessment.recommended_actions.forEach(action => {
      html += `<li>${action}</li>`;
    });
    html += `</ul>`;
  }
  
  html += `</div></div>
  
  <!-- Feedback Section -->
  <div style="margin-top: 20px; padding: 15px; background: #e8f4f8; border-radius: 4px; border: 1px solid #b3d9e8;">
    <h4 style="margin-top: 0; color: #0066cc;">📝 Assessment Review & Feedback</h4>
    <p style="font-size: 13px; color: #666;">Disagree with this assessment? Help improve the AI by providing feedback.</p>
    
    <div style="margin-bottom: 10px;">
      <label style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <input type="radio" name="feedback-level-${reportId}" value="too-harsh" style="margin: 0;"> Risk level is TOO HARSH
      </label>
      <label style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <input type="radio" name="feedback-level-${reportId}" value="too-lenient" style="margin: 0;"> Risk level is TOO LENIENT
      </label>
      <label style="display: flex; align-items: center; gap: 10px;">
        <input type="radio" name="feedback-level-${reportId}" value="accurate" style="margin: 0;"> Assessment is ACCURATE
      </label>
    </div>
    
    <textarea id="feedback-text-${reportId}" placeholder="Additional comments (optional)..." style="width: 100%; padding: 8px; border: 1px solid #bbb; border-radius: 4px; margin-bottom: 10px;"></textarea>
    
    <button type="button" onclick="submitFeedback('${reportId}')" style="background: #0066cc; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; width: auto; margin-right: 10px;">Submit Feedback</button>
    <span id="feedback-status-${reportId}" style="color: #666; font-size: 13px;"></span>
  </div>
  
  </div>`;
  return html;
}

document.getElementById("reportForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const category = document.querySelector("select").value;
  const description = document.querySelector("textarea").value;
  const location = document.getElementById("locationInput").value;
  const fileInput = document.querySelector("input[type=file]");
  const submitBtn = e.target.querySelector("button[type=submit]");

  let image = null;
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    
    // Check file size (max 5MB for base64)
    if (file.size > 5 * 1024 * 1024) {
      alert("Image too large! Please upload an image smaller than 5MB.");
      return;
    }
    
    const reader = new FileReader();
    reader.onload = async (event) => {
      let image = event.target.result; // base64 encoded image
      
      // Compress image before sending
      console.log("Original image size:", Math.round(image.length / 1024), "KB");
      image = await compressImage(image, 800, 0.65);
      console.log("Compressed image size:", Math.round(image.length / 1024), "KB");
      
      console.log("Submitting:", {category, description, location});
      
      // Update button to show loading
      submitBtn.disabled = true;
      submitBtn.textContent = "📊 Analyzing with AI...";

      try {
        const response = await fetch("/submit-report", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({category, description, location, image})
        });

        const data = await response.json();
        console.log("Response:", data);

        if (response.ok) {
          const reportId = data.id;
          const riskHTML = displayRiskAssessment(data.risk_assessment, image, reportId);
          
          // Show success message
          alert(`✅ Report saved! ID: ${reportId}`);
          
          // Clear form
          document.getElementById("reportForm").reset();
          
          // Show risk assessment section
          const riskSection = document.getElementById("riskAssessmentSection");
          const riskContainer = document.getElementById("riskAssessmentContainer");
          
          // Clear previous assessment
          riskContainer.innerHTML = "";
          
          // Display new risk assessment in dedicated section
          if (riskHTML) {
            riskContainer.innerHTML = riskHTML;
            riskSection.style.display = "block";
            
            // Scroll to risk assessment section
            riskSection.scrollIntoView({ behavior: "smooth", block: "start" });
          }
          
          // Reset button
          submitBtn.disabled = false;
          submitBtn.textContent = "Submit Report";
        } else {
          alert("❌ Error: " + data.message);
          submitBtn.disabled = false;
          submitBtn.textContent = "Submit Report";
        }
      } catch (error) {
        console.error("Fetch error:", error);
        alert("⚠️ Failed to submit: " + error.message);
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Report";
      }
    };
    reader.readAsDataURL(file);
  } else {
    alert("Please select an image");
  }
});
