const analyzeBtn = document.getElementById("analyzeBtn");
const resumeFile = document.getElementById("resumeFile");
const result = document.getElementById("result");

analyzeBtn.addEventListener("click", async () => {

    if (!resumeFile.files.length) {
        result.innerHTML = "<p>Please select a PDF resume first.</p>";
        return;
    }

    const file = resumeFile.files[0];
    const jobDescription = document.getElementById("jobDescription").value;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);

    result.innerHTML = "<p>Analyzing resume...</p>";

    try {
        const response = await fetch("https://ai-resume-analyzer-7ccz.onrender.com/upload_resume", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        if (!response.ok) {
            result.innerHTML = "<p>Something went wrong.</p>";
            return;
        }

        result.innerHTML = `
    <div class="score-card">
        <h2>Resume Score</h2>
        <div class="score-number">${data.resume_score}/100</div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: ${data.resume_score}%"></div>
        </div>
    </div>

    <div class="analysis-grid">
        <div class="info-card">
            <h3>Skills Found</h3>
            <div class="tags">
                ${
                    data.found_skills.length
                        ? data.found_skills.map(skill => `<span>${skill}</span>`).join("")
                        : "<p>No matching skills found.</p>"
                }
            </div>
        </div>

        <div class="info-card">
            <h3>Missing Sections</h3>
            <div class="tags">
                ${
                    data.missing_sections.length
                        ? data.missing_sections.map(section => `<span>${section}</span>`).join("")
                        : "<p>No major sections missing.</p>"
                }
            </div>
        </div>
    </div>

    ${jobDescription.trim() ? `
    <div class="info-card">
        <h3>Job Match Score</h3>

        <div class="score-number">
            ${data.job_match_score}%
        </div>
        <p class="match-label">${data.match_label}</p>

        <div class="progress-bar">
            <div class="progress-fill"
                 style="width: ${data.job_match_score}%">
            </div>
        </div>

        <h3>Matching Skills</h3>
        <div class="tags">
            ${
                data.matching_skills.length
                    ? data.matching_skills
                        .map(skill => `<span>${skill}</span>`)
                        .join("")
                    : "<p>No matching skills found.</p>"
            }
        </div>

        <h3>Missing Job Skills</h3>
        <div class="tags">
            ${
                data.missing_job_skills.length
                    ? data.missing_job_skills
                        .map(skill => `<span>${skill}</span>`)
                        .join("")
                    : "<p>No missing job skills.</p>"
            }
        </div>
    </div>
` : ""}

    <div class="info-card suggestions-card">
        <h3>Suggestions</h3>
        <ul>
            ${data.suggestions.map(item => `<li>${item}</li>`).join("")}
        </ul>
    </div>
`;

    } catch (error) {
        result.innerHTML = "<p>Could not connect to the server.</p>";
        console.error(error);
    }
});


const fileInfo = document.getElementById("fileInfo");

resumeFile.addEventListener("change", function () {
    if (resumeFile.files.length > 0) {
        fileInfo.textContent = "Selected: " + resumeFile.files[0].name;
    }
});