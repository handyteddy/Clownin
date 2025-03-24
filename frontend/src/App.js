import React, { useState } from "react";
import axios from "axios";

export default function App() {
    const [videoPath, setVideoPath] = useState(null);
    const [faces, setFaces] = useState([]);
    const [selectedFaces, setSelectedFaces] = useState([]);
    const [overlayType, setOverlayType] = useState("clown");
    const [processedVideo, setProcessedVideo] = useState(null);

    const uploadVideo = async (event) => {
        const file = event.target.files[0];
        const formData = new FormData();
        formData.append("file", file);
        const res = await axios.post("http://localhost:8000/upload/", formData);
        setVideoPath(res.data.filename);
        extractFaces(res.data.filename);
    };

    const extractFaces = async (videoPath) => {
        const res = await axios.post("http://localhost:8000/extract_faces/", { video_path: videoPath });
        if (res.data.faces) {
            setFaces(res.data.faces);
        }
    };

    const applyOverlay = async () => {
        const res = await axios.post("http://localhost:8000/apply_overlay/", {
            video_path: videoPath,
            face_index: selectedFaces,
            overlay_type: overlayType,
        });
        if (res.data.processed_video) {
            setProcessedVideo(res.data.processed_video);
        }
    };

    return (
        <div>
            <h1>Video Face Overlay App</h1>
            <input type="file" accept="video/*" onChange={uploadVideo} />
            <div>
                {faces.map((face, index) => (
                    <img
                        key={index}
                        src={`http://localhost:8000/${face}`}
                        alt={`Face ${index}`}
                        onClick={() => setSelectedFaces([...selectedFaces, index])}
                        style={{ border: selectedFaces.includes(index) ? "2px solid red" : "none" }}
                    />
                ))}
            </div>
            <select onChange={(e) => setOverlayType(e.target.value)}>
                <option value="clown">Clown</option>
                <option value="political">Political</option>
                <option value="comical">Comical</option>
            </select>
            <button onClick={applyOverlay}>Apply Overlay</button>
            {processedVideo && <video src={`http://localhost:8000/${processedVideo}`} controls />}
        </div>
    );
}
