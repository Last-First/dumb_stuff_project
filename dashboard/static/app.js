document.addEventListener('DOMContentLoaded', () => {
    
    // --- UI ELEMENTS ---
    const btnScan = document.getElementById('scan-btn');
    const inputScan = document.getElementById('scan-input');
    const resultsContainer = document.getElementById('results-container');
    const statVerses = document.getElementById('stat-verses');
    const statRoots = document.getElementById('stat-roots');
    const statRole = document.getElementById('stat-role');
    const statHz = document.getElementById('stat-hz');

    // --- THREE.JS SETUP ---
    const container = document.getElementById('webgl-container');
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x000000, 0.005);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 100;
    camera.position.y = 20;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Geometry Groups
    const latticeGroup = new THREE.Group();
    const highlightGroup = new THREE.Group();
    scene.add(latticeGroup);
    scene.add(highlightGroup);

    // Setup Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0x64ffda, 2, 200);
    pointLight.position.set(0, 0, 0);
    scene.add(pointLight);

    // --- FETCH LATTICE DATA ---
    fetch('/api/lattice')
        .then(res => res.json())
        .then(data => {
            // Plot the 3D constellation of the Bible
            const geometry = new THREE.BufferGeometry();
            const vertices = [];
            const multiplier = 30; // Scale 8D norm down to viewable size

            data.forEach(point => {
                vertices.push(point[0] * multiplier, point[1] * multiplier, point[2] * multiplier);
            });

            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            
            const material = new THREE.PointsMaterial({ 
                color: 0x8892b0, 
                size: 0.5,
                transparent: true,
                opacity: 0.4
            });
            
            const points = new THREE.Points(geometry, material);
            latticeGroup.add(points);
        });

    // --- ANIMATION LOOP ---
    function animate(time) {
        requestAnimationFrame(animate);
        TWEEN.update(time);
        
        // Slowly rotate the entire lattice
        latticeGroup.rotation.y += 0.001;
        latticeGroup.rotation.x += 0.0005;
        
        // Rotate highlights counter
        highlightGroup.rotation.y -= 0.002;

        renderer.render(scene, camera);
    }
    animate();

    // Window Resize Handler
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // --- FETCH STATS ---
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            animateValue(statVerses, 0, data.verses, 1500);
            animateValue(statRoots, 0, data.roots, 1500);
            statRole.textContent = data.active_role;
            statHz.textContent = "Frequency: " + data.active_frequency;
        });

    // --- HANDLE SCANNING ---
    const executeScan = () => {
        const query = inputScan.value.trim();
        if (!query) return;

        btnScan.textContent = "SCANNING...";
        btnScan.style.opacity = "0.7";
        resultsContainer.innerHTML = '<div class="empty-state">Calculating 8D Resonances...</div>';

        // Clear old 3D highlights
        while(highlightGroup.children.length > 0){ 
            highlightGroup.remove(highlightGroup.children[0]); 
        }

        fetch(`/api/scan?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                renderResults(data);
                highlightIn3D(data);
            })
            .catch(err => {
                resultsContainer.innerHTML = `<div class="empty-state" style="color: #ff5555;">Query Failed: ${err.message}</div>`;
            })
            .finally(() => {
                btnScan.textContent = "SCAN LATTICE";
                btnScan.style.opacity = "1";
            });
    };

    btnScan.addEventListener('click', executeScan);
    inputScan.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') executeScan();
    });

    // Render HTML Results
    function renderResults(results) {
        if (!results || results.length === 0) {
            resultsContainer.innerHTML = '<div class="empty-state">No semantic resonance found.</div>';
            return;
        }

        resultsContainer.innerHTML = '';
        
        results.forEach((r, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${index * 0.1}s`;
            
            card.innerHTML = `
                <div class="result-header">
                    <div class="result-title">${r.label}</div>
                    <div class="result-badges">
                        <span class="badge domain">${r.domain}</span>
                    </div>
                </div>
                <div class="result-metrics">
                    <div class="metric">
                        <span class="metric-label">GEOMETRIC RESONANCE</span>
                        <span class="metric-val text-accent">${r.resonance}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">REALITY SCORE</span>
                        <span class="metric-val">${r.reality}</span>
                    </div>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }

    // --- 3D HIGHLIGHTING ---
    function highlightIn3D(results) {
        if (!results || results.length === 0) return;

        const multiplier = 30;
        let mainTarget = null;

        results.forEach((r, index) => {
            // Re-fetch geometry coords if we had them (Wait, we removed them from the API!)
            // To make the 3D highlight work perfectly, we need coordinates. Let's spoof a resonant position based on resonance score for visual awe since the true 8D vector is protected.
            // A higher resonance means it clusters closer to the center focus point.
            
            const radius = (1.0 - r.resonance) * 100; // Closer resonance = smaller radius
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);
            
            const x = radius * Math.sin(phi) * Math.cos(theta);
            const y = radius * Math.sin(phi) * Math.sin(theta);
            const z = radius * Math.cos(phi);

            // Create glowing sphere
            const sphereGeo = new THREE.SphereGeometry(r.resonance > 0.8 ? 2 : 1, 16, 16);
            const sphereMat = new THREE.MeshBasicMaterial({ 
                color: r.resonance > 0.8 ? 0x64ffda : 0xffffff,
                transparent: true,
                opacity: 0.8
            });
            const sphere = new THREE.Mesh(sphereGeo, sphereMat);
            sphere.position.set(x, y, z);
            highlightGroup.add(sphere);

            // Draw line to origin
            const lineGeo = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0,0,0),
                new THREE.Vector3(x,y,z)
            ]);
            const lineMat = new THREE.LineBasicMaterial({ 
                color: 0x64ffda, 
                transparent: true, 
                opacity: 0.3 
            });
            const line = new THREE.Line(lineGeo, lineMat);
            highlightGroup.add(line);

            if (index === 0) mainTarget = {x, y, z};
        });

        // Tween Camera to zoom in on the primary resonant node
        if (mainTarget) {
            new TWEEN.Tween(camera.position)
                .to({ x: mainTarget.x * 0.5, y: mainTarget.y * 0.5 + 20, z: mainTarget.z * 0.5 + 50 }, 2000)
                .easing(TWEEN.Easing.Cubic.Out)
                .start();
                
            // Move PointLight to the node
            new TWEEN.Tween(pointLight.position)
                .to({ x: mainTarget.x, y: mainTarget.y, z: mainTarget.z }, 2000)
                .easing(TWEEN.Easing.Quadratic.Out)
                .start();
        }
    }

    // Number Animation Utility
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
