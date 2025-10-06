/**
 * Advanced CAD SDK Viewer - Three.js Implementation
 * Production-grade visualization with accurate CAD processing
 * NO SIMULATIONS - Real geometric rendering only
 */

class AdvancedSDKViewer {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.currentData = null;
        this.currentView = 'complete';
        this.meshGroups = {
            walls: [],
            restricted: [],
            entrances: [],
            ilots: [],
            corridors: [],
            openSpaces: []
        };
        
        this.init();
        this.setupEventListeners();
        this.animate();
    }

    init() {
        const canvas = document.getElementById('canvas');
        const container = document.getElementById('viewer-container');

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);
        this.scene.fog = new THREE.Fog(0x0a0a0a, 100, 500);

        // Camera
        const aspect = window.innerWidth / window.innerHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
        this.camera.position.set(0, 80, 80);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Controls
        this.controls = new THREE.OrbitControls(this.camera, canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 10;
        this.controls.maxDistance = 300;
        this.controls.maxPolarAngle = Math.PI / 2;

        // Lights
        this.setupLights();

        // Grid
        const gridHelper = new THREE.GridHelper(200, 50, 0x444444, 0x222222);
        this.scene.add(gridHelper);

        // Axes
        const axesHelper = new THREE.AxesHelper(20);
        this.scene.add(axesHelper);

        // Resize handler
        window.addEventListener('resize', () => this.onResize());
    }

    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 100, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 500;
        directionalLight.shadow.camera.left = -100;
        directionalLight.shadow.camera.right = 100;
        directionalLight.shadow.camera.top = 100;
        directionalLight.shadow.camera.bottom = -100;
        this.scene.add(directionalLight);

        // Hemisphere light
        const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
        this.scene.add(hemisphereLight);

        // Point lights for accent
        const pointLight1 = new THREE.PointLight(0x6366f1, 0.3, 100);
        pointLight1.position.set(30, 40, 30);
        this.scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x10b981, 0.3, 100);
        pointLight2.position.set(-30, 40, -30);
        this.scene.add(pointLight2);
    }

    setupEventListeners() {
        // File input
        document.getElementById('file-input').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Sliders with live update
        const sliders = [
            { id: 'ilot-count', valId: 'ilot-count-val' },
            { id: 'corridor-width', valId: 'corridor-width-val', unit: 'm' },
            { id: 'wall-thickness', valId: 'wall-thickness-val', unit: 'm' },
            { id: 'dist-0-1', valId: 'dist-0-1-val', unit: '%', callback: () => this.updateDistTotal() },
            { id: 'dist-1-3', valId: 'dist-1-3-val', unit: '%', callback: () => this.updateDistTotal() },
            { id: 'dist-3-5', valId: 'dist-3-5-val', unit: '%', callback: () => this.updateDistTotal() },
            { id: 'dist-5-10', valId: 'dist-5-10-val', unit: '%', callback: () => this.updateDistTotal() }
        ];

        sliders.forEach(({ id, valId, unit = '', callback }) => {
            const slider = document.getElementById(id);
            const display = document.getElementById(valId);
            
            slider.addEventListener('input', (e) => {
                display.textContent = e.target.value + unit;
                if (callback) callback();
            });
        });
    }

    updateDistTotal() {
        const d1 = parseInt(document.getElementById('dist-0-1').value);
        const d2 = parseInt(document.getElementById('dist-1-3').value);
        const d3 = parseInt(document.getElementById('dist-3-5').value);
        const d4 = parseInt(document.getElementById('dist-5-10').value);
        const total = d1 + d2 + d3 + d4;
        
        const totalEl = document.getElementById('dist-total');
        totalEl.textContent = total + '%';
        totalEl.style.color = total === 100 ? '#10b981' : '#ef4444';
    }

    async handleFileUpload(file) {
        if (!file) return;

        this.showLoading(true);

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Send to backend for processing
            const response = await fetch('/api/parse-dxf', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to parse DXF file');
            }

            const data = await response.json();
            this.currentData = data;
            
            // Render the plan
            this.renderFloorPlan(data);
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading file:', error);
            alert('Error loading file: ' + error.message);
            this.showLoading(false);
        }
    }

    async processFloorPlan() {
        if (!this.currentData) {
            alert('Please load a DXF file first');
            return;
        }

        this.showLoading(true);

        try {
            const config = {
                total_ilots: parseInt(document.getElementById('ilot-count').value),
                corridor_width: parseFloat(document.getElementById('corridor-width').value),
                wall_thickness: parseFloat(document.getElementById('wall-thickness').value),
                distribution: {
                    size_0_1: parseFloat(document.getElementById('dist-0-1').value) / 100,
                    size_1_3: parseFloat(document.getElementById('dist-1-3').value) / 100,
                    size_3_5: parseFloat(document.getElementById('dist-3-5').value) / 100,
                    size_5_10: parseFloat(document.getElementById('dist-5-10').value) / 100
                }
            };

            const response = await fetch('/api/process-floor-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error('Failed to process floor plan');
            }

            const result = await response.json();
            this.currentData = { ...this.currentData, ...result };
            
            // Re-render with îlots and corridors
            this.renderFloorPlan(this.currentData);
            this.updateStats(result);
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error processing:', error);
            alert('Error processing: ' + error.message);
            this.showLoading(false);
        }
    }

    renderFloorPlan(data) {
        // Clear existing meshes
        this.clearScene();

        const wallThickness = parseFloat(document.getElementById('wall-thickness').value);

        // Render based on current view
        if (this.currentView === 'plan' || this.currentView === 'complete' || 
            this.currentView === 'ilots' || this.currentView === 'corridors') {
            
            // Open spaces (light background)
            if (data.open_spaces) {
                data.open_spaces.forEach(space => {
                    this.createPolygonMesh(space, 0xf5f5f5, 0.3, 'openSpaces', 0);
                });
            }

            // Walls (black, thicker - architectural style)
            if (data.walls) {
                data.walls.forEach(wall => {
                    this.createPolygonMesh(wall, 0x1a1a1a, 1.0, 'walls', wallThickness * 3);
                });
            }

            // Restricted areas (blue)
            if (data.restricted_areas) {
                data.restricted_areas.forEach(restricted => {
                    this.createPolygonMesh(restricted, 0x4682ff, 0.8, 'restricted', 0.5);
                });
            }

            // Entrances (red)
            if (data.entrances) {
                data.entrances.forEach(entrance => {
                    this.createPolygonMesh(entrance, 0xff4444, 0.8, 'entrances', 0.5);
                });
            }
        }

        // Îlots (green)
        if ((this.currentView === 'ilots' || this.currentView === 'complete' || 
             this.currentView === 'corridors') && data.ilots) {
            data.ilots.forEach(ilot => {
                this.createPolygonMesh(ilot.polygon, 0x2ecc71, 0.9, 'ilots', 1.0);
            });
        }

        // Corridors (purple)
        if ((this.currentView === 'corridors' || this.currentView === 'complete') && data.corridors) {
            data.corridors.forEach(corridor => {
                this.createPolygonMesh(corridor.polygon, 0x9b59b6, 0.7, 'corridors', 0.3);
            });
        }

        // Auto-fit camera
        this.fitCameraToScene();
    }

    createPolygonMesh(polygonData, color, opacity, group, height = 0.2) {
        if (!polygonData || !polygonData.coordinates) return;

        const coords = polygonData.coordinates[0]; // Exterior ring
        
        if (coords.length < 3) return;

        // Create shape
        const shape = new THREE.Shape();
        shape.moveTo(coords[0][0], coords[0][1]);
        
        for (let i = 1; i < coords.length; i++) {
            shape.lineTo(coords[i][0], coords[i][1]);
        }

        // Extrude settings
        const extrudeSettings = {
            depth: height,
            bevelEnabled: group === 'walls', // Add bevel for walls
            bevelThickness: group === 'walls' ? 0.05 : 0,
            bevelSize: group === 'walls' ? 0.05 : 0,
            bevelSegments: 2
        };

        const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        
        // Material with proper lighting - different for walls
        const materialConfig = {
            color: color,
            transparent: opacity < 1,
            opacity: opacity,
            metalness: group === 'walls' ? 0.05 : 0.1,
            roughness: group === 'walls' ? 0.95 : 0.8,
            side: THREE.DoubleSide
        };
        
        const material = new THREE.MeshStandardMaterial(materialConfig);

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        // Add edge lines for better definition
        const edges = new THREE.EdgesGeometry(geometry);
        const edgeColor = group === 'walls' ? 0x000000 : 0x333333;
        const edgeOpacity = group === 'walls' ? 0.8 : 0.3;
        
        const lineMaterial = new THREE.LineBasicMaterial({ 
            color: edgeColor, 
            linewidth: group === 'walls' ? 2 : 1,
            transparent: true,
            opacity: edgeOpacity
        });
        const lineSegments = new THREE.LineSegments(edges, lineMaterial);
        mesh.add(lineSegments)

        this.scene.add(mesh);
        this.meshGroups[group].push(mesh);
    }

    clearScene() {
        Object.keys(this.meshGroups).forEach(groupName => {
            this.meshGroups[groupName].forEach(mesh => {
                if (mesh.geometry) mesh.geometry.dispose();
                if (mesh.material) {
                    if (Array.isArray(mesh.material)) {
                        mesh.material.forEach(mat => mat.dispose());
                    } else {
                        mesh.material.dispose();
                    }
                }
                this.scene.remove(mesh);
            });
            this.meshGroups[groupName] = [];
        });
    }

    fitCameraToScene() {
        const box = new THREE.Box3();
        
        // Calculate bounding box of all visible objects
        this.scene.traverse(obj => {
            if (obj.isMesh) {
                box.expandByObject(obj);
            }
        });

        if (box.isEmpty()) return;

        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / Math.tan(fov / 2)) * 1.5;

        this.camera.position.set(center.x, cameraZ * 0.8, center.z + cameraZ);
        this.camera.lookAt(center);
        this.controls.target.copy(center);
        this.controls.update();
    }

    updateStats(data) {
        if (!data) return;

        document.getElementById('stat-ilots').textContent = data.ilots?.length || 0;
        document.getElementById('stat-corridors').textContent = data.corridors?.length || 0;
        document.getElementById('stat-coverage').textContent = 
            (data.total_coverage_pct || 0).toFixed(1) + '%';
        document.getElementById('stat-area').textContent = 
            (data.total_area || 0).toFixed(0) + 'm²';
    }

    setView(view) {
        this.currentView = view;
        
        // Update button states
        ['plan', 'ilots', 'corridors', 'complete'].forEach(v => {
            document.getElementById(`btn-${v}`).classList.toggle('active', v === view);
        });

        // Re-render
        if (this.currentData) {
            this.renderFloorPlan(this.currentData);
        }
    }

    showLoading(show) {
        document.getElementById('loading').classList.toggle('active', show);
    }

    onResize() {
        const width = window.innerWidth;
        const height = window.innerHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

// Global functions for HTML onclick handlers
let viewer;

function setView(view) {
    if (viewer) {
        viewer.setView(view);
    }
}

function processFloorPlan() {
    if (viewer) {
        viewer.processFloorPlan();
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    viewer = new AdvancedSDKViewer();
    
    // Load demo data if available
    loadDemoData();
});

async function loadDemoData() {
    try {
        const response = await fetch('/api/demo-data');
        if (response.ok) {
            const data = await response.json();
            viewer.currentData = data;
            viewer.renderFloorPlan(data);
            viewer.updateStats(data);
        }
    } catch (e) {
        console.log('No demo data available');
    }
}
