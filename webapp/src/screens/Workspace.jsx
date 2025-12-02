import React from 'react';
import { VitePreview } from '../components/VitePreview';
import TopBar from '../components/TopBar';
import './Workspace.css';

function Workspace() {
    return (
        <div className="workspace">
            <TopBar title="Workspace" showBack={false} />
            <div className="workspace__content">
                <VitePreview />
            </div>
        </div>
    );
}

export default Workspace;
