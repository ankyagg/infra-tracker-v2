// --- GUARD CLAUSE ---
if (!document.getElementById("reportForm")) {
  console.log("On Landing Page - Script standby.");
} else {
  
  // 1. File Upload UI Interaction
  document.getElementById("fileInput").addEventListener("change", function(e) {
    const fileName = e.target.files[0]?.name;
    const visualText = document.getElementById("fileText");
    const visualIcon = document.querySelector("#fileVisual i");
    
    if (fileName) {
      visualText.textContent = "Selected: " + fileName;
      visualText.style.fontWeight = "bold";
      visualText.style.color = "#28a745";
      visualIcon.classList.remove("fa-cloud-arrow-up");
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

  // 4. Render Results
  function displayResult(data, image, id) {
    const riskLevel = data?.risk_level || 0;
    const urgency = data?.urgency || "Review Needed";
    const damageType = data?.damage_type || "Analysis pending";
    
    let actionsHTML = "";
    if (data?.recommended_actions && Array.isArray(data.recommended_actions)) {
      actionsHTML = data.recommended_actions.map(a => `<li>${a}</li>`).join('');
    } else {
      actionsHTML = "<li>No specific actions recommended by AI.</li>";
    }

    const colors = {
      1: "#28a745", 2: "#8bc34a", 3: "#ffc107", 4: "#fd7e14", 5: "#dc3545"
    };
    const theme = colors[riskLevel] || "#6c757d";

    return `
      <section class="app-card" style="border-top: 6px solid ${theme}; animation: slideUp 0.6s ease;">
        <div class="result-header">
          <h2 style="margin:0; color:${theme}; display: flex; align-items: center; gap: 10px;">
            <i class="fa-solid fa-triangle-exclamation"></i> 
            Risk Level: ${riskLevel}/5
          </h2>
          <span style="background:${theme}; color:white; padding:6px 14px; border-radius:20px; font-size:0.85rem; font-weight: 700;">
            ${urgency.toUpperCase()}
          </span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top:20px;">
          <div>
            <img src="${image}" style="width:100%; border-radius:12px; border:2px solid #eee;">
            <p style="font-size: 0.8rem; color: #999; margin-top: 10px; text-align: center;">Ref ID: ${id}</p>
          </div>
          <div>
            <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; border: 1px solid #e9ecef;">
              <h4 style="margin-top:0; color: #0a192f; border-bottom: 2px solid #e1e4e8; padding-bottom: 12px;">
                <i class="fa-solid fa-robot"></i> AI Assessment
              </h4>
              <p style="margin-bottom: 5px; font-size: 0.9rem; color: #666; text-transform: uppercase; font-weight: bold;">Detected Issue</p>
              <p style="font-size: 1.1rem; margin-top: 0; font-weight: 500;">${damageType}</p>
              <p style="margin-bottom: 5px; font-size: 0.9rem; color: #666; text-transform: uppercase; font-weight: bold;">Recommended Actions</p>
              <ul style="padding-left:20px; color:#444; margin-top: 0; line-height: 1.6;">${actionsHTML}</ul>
              <button onclick="window.location.reload()" 
                style="margin-top:20px; width: 100%; background: white; color: ${theme}; border: 2px solid ${theme}; padding: 12px; cursor: pointer; border-radius: 8px; font-weight: 700;">
                <i class="fa-solid fa-rotate-right"></i> Submit New Report
              </button>
            </div>
          </div>
        </div>
      </section>
    `;
  }

  // 5. Form Submission Logic
  document.getElementById("reportForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
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
        const response = await fetch("/submit-report", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
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