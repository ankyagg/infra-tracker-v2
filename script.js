// --- GUARD CLAUSE ---
if (!document.getElementById("reportForm")) {
  console.log("On Landing Page - Script standby.");
} else {
  // Block unauthenticated access to the report page immediately
  const initialToken = localStorage.getItem('userToken');
  if (!initialToken) {
    // Send user to login/signup before they can see the report form
    window.location.href = 'login.html';
  } else {
    // Verify token in background and redirect if invalid
    (async () => {
      try {
        const rv = await fetch('/auth/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: initialToken })
        });
        const rj = await rv.json();
        if (rj.status !== 'success' || !rj.valid) {
          localStorage.removeItem('userToken');
          window.location.href = 'login.html';
        }
      } catch (err) {
        console.error('Auth verify failed:', err);
        // If verification fails due to network, keep user on page for now
      }
    })();
  }
  
  // 1. File Upload UI Interaction (Camera Capture)
  document.getElementById("fileInput").addEventListener("change", function(e) {
    const file = e.target.files[0];
    const visualText = document.getElementById("fileText");
    const visualIcon = document.querySelector("#fileVisual i");
    
    if (file) {
      // Show image preview info
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
      visualText.textContent = `Photo captured (${fileSizeMB} MB)`;
      visualText.style.fontWeight = "bold";
      visualText.style.color = "#28a745";
      visualIcon.classList.remove("fa-camera");
      visualIcon.classList.add("fa-check-circle");
      visualIcon.style.color = "#28a745";
    }
  });

  // 2. Location Feature
  document.getElementById("getLocationBtn").addEventListener("click", function() {
    const btn = this;
    const input = document.getElementById("locationInput");
    
    if ("geolocation" in navigator) {
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
      btn.disabled = true;
      
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          input.value = `${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)}`;
          btn.innerHTML = '<i class="fa-solid fa-check"></i>';
          btn.style.background = "#28a745";
          btn.disabled = false;
        },
        (err) => {
          console.error(err);
          alert("Could not get location. Please allow GPS access.");
          btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i>';
          btn.style.background = "var(--navy-light)";
          btn.disabled = false;
        }
      );
    } else {
      alert("Geolocation is not supported by your browser.");
    }
  });

  // 3. Image Compression Helper
  function compressImage(base64Image) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        const maxWidth = 800;
        let w = img.width;
        let h = img.height;
        
        if (w > maxWidth) {
          h = (maxWidth / w) * h;
          w = maxWidth;
        }
        
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL("image/jpeg", 0.7));
      };
      img.src = base64Image;
    });
  }

  // 4. Render Results - Redesigned for better mobile experience
  function displayResult(data, image, id) {
    const riskLevel = data?.risk_level || 0;
    const safetyRisk = data?.safety_risk || riskLevel;
    const urgency = data?.urgency || "Review Needed";
    const damageType = data?.damage_type || "Analysis pending";
    
    let actionsHTML = "";
    if (data?.recommended_actions && Array.isArray(data.recommended_actions)) {
      actionsHTML = data.recommended_actions.map(a => `
        <div class="action-item">
          <i class="fa-solid fa-circle-check"></i>
          <span>${a}</span>
        </div>
      `).join('');
    } else {
      actionsHTML = `<div class="action-item"><i class="fa-solid fa-circle-info"></i><span>No specific actions recommended.</span></div>`;
    }

    const colors = {
      1: "#22c55e", 2: "#84cc16", 3: "#eab308", 4: "#f97316", 5: "#ef4444"
    };
    const bgColors = {
      1: "#f0fdf4", 2: "#f7fee7", 3: "#fefce8", 4: "#fff7ed", 5: "#fef2f2"
    };
    const labels = {
      1: "Very Low", 2: "Low", 3: "Moderate", 4: "High", 5: "Critical"
    };
    const theme = colors[riskLevel] || "#6b7280";
    const bgTheme = bgColors[riskLevel] || "#f9fafb";
    const riskLabel = labels[riskLevel] || "Unknown";

    return `
      <section class="result-card">
        <!-- Success Header -->
        <div class="result-success-banner">
          <i class="fa-solid fa-circle-check"></i>
          <span>Report Submitted Successfully</span>
        </div>

        <!-- Risk Score Section -->
        <div class="risk-score-section" style="background: ${bgTheme}; border-color: ${theme};">
          <div class="risk-score-circle" style="border-color: ${theme}; color: ${theme};">
            <span class="risk-number">${riskLevel}</span>
            <span class="risk-max">/5</span>
          </div>
          <div class="risk-info">
            <span class="risk-label" style="color: ${theme};">${riskLabel} Risk</span>
            <span class="urgency-badge" style="background: ${theme};">${urgency.toUpperCase()}</span>
          </div>
        </div>

        <!-- Image Preview -->
        <div class="result-image-container">
          <img src="${image}" alt="Captured Evidence" class="result-image">
          <div class="result-image-overlay">
            <i class="fa-solid fa-image"></i> Evidence Captured
          </div>
        </div>

        <!-- AI Analysis Card -->
        <div class="ai-analysis-card">
          <div class="ai-header">
            <div class="ai-icon">
              <i class="fa-solid fa-brain"></i>
            </div>
            <div>
              <h3>AI Analysis</h3>
              <p>Powered by Gemini</p>
            </div>
          </div>

          <div class="analysis-item">
            <div class="analysis-label">
              <i class="fa-solid fa-magnifying-glass-chart"></i>
              Detected Issue
            </div>
            <div class="analysis-value">${damageType}</div>
          </div>

          <div class="analysis-item">
            <div class="analysis-label">
              <i class="fa-solid fa-shield-halved"></i>
              Safety Risk Level
            </div>
            <div class="safety-bar-container">
              <div class="safety-bar" style="width: ${(safetyRisk/5)*100}%; background: ${theme};"></div>
            </div>
            <span class="safety-value" style="color: ${theme};">${safetyRisk}/5</span>
          </div>

          <div class="analysis-item">
            <div class="analysis-label">
              <i class="fa-solid fa-list-check"></i>
              Recommended Actions
            </div>
            <div class="actions-list">
              ${actionsHTML}
            </div>
          </div>
        </div>

        <!-- Report ID -->
        <div class="report-id-section">
          <span><i class="fa-solid fa-hashtag"></i> Report ID</span>
          <code>${id}</code>
        </div>

        <!-- Action Buttons -->
        <div class="result-actions">
          <button onclick="window.location.reload()" class="btn-new-report">
            <i class="fa-solid fa-plus"></i>
            Submit New Report
          </button>
          <button onclick="window.location.href='index.html'" class="btn-home">
            <i class="fa-solid fa-house"></i>
            Home
          </button>
        </div>
      </section>
    `;
  }

  // 5. Form Submission Logic
  document.getElementById("reportForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    // Redirect unauthenticated users to signup/login
    const token = localStorage.getItem('userToken');
    if (!token) {
      // Preserve intent: send user to signup tab
      window.location.href = 'login.html#signup';
      return;
    }
    
    const btn = document.querySelector(".analyze-btn");
    const originalBtnText = btn.innerHTML;
    const fileInput = document.getElementById("fileInput");
    
    if (fileInput.files.length === 0) return alert("Please upload an image evidence.");

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing Infrastructure...';
    btn.style.opacity = "0.8";

    const reader = new FileReader();
    reader.readAsDataURL(fileInput.files[0]);
    
    reader.onload = async (event) => {
      try {
        const compressedImage = await compressImage(event.target.result);
        
        const payload = {
          category: document.querySelector("select").value,
          description: document.querySelector("textarea").value,
          location: document.getElementById("locationInput").value,
          image: compressedImage
        };

        // CORRECTED: Use relative path (automatically uses current domain/port)
        // Include Authorization header if token present
        const clientToken = localStorage.getItem('userToken');
        const headers = { "Content-Type": "application/json" };
        if (clientToken) headers['Authorization'] = `Bearer ${clientToken}`;

        const response = await fetch("/submit-report", {
          method: "POST",
          headers,
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === "success") {
          document.getElementById("formSection").style.display = "none";
          const container = document.getElementById("riskResultContainer");
          container.innerHTML = displayResult(data.risk_assessment, compressedImage, data.id);
        } else {
          throw new Error(data.message || "Unknown server error");
        }

      } catch (err) {
        console.error("Submission Error:", err);
        alert("⚠️ Analysis Failed: " + err.message);
        btn.disabled = false;
        btn.innerHTML = originalBtnText;
        btn.style.opacity = "1";
      }
    };
  });
}