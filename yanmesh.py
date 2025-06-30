import gradio as gr
import trimesh
import plotly.graph_objects as go
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Paths to default files
DEFAULT_MESH_PATH = "data/bunny.obj"
DEFAULT_META_PATH = "data/bunny.json"
STATS_NOT_FOUND = {'Error': 'No data to show'}


def mesh_to_plot(mesh_path):
    try:
        mesh = trimesh.load(mesh_path, force='mesh')
        logging.info(f"Loaded mesh from {mesh_path} for Plotly.")
        x, y, z = mesh.vertices.T
        i, j, k = mesh.faces.T
        fig = go.Figure(
            data=[
                go.Mesh3d(
                    x=x, y=y, z=z,
                    i=i, j=j, k=k,
                    color='lightblue', opacity=0.9
                )
            ]
        )
        fig.update_layout(
            scene=dict(aspectmode='data'),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        return fig, mesh
    except Exception as e:
        logging.error(f"Failed to load/plot mesh: {e}")
        return go.Figure(), None


def load_mesh_stats(mesh_path):
    _, mesh = mesh_to_plot(mesh_path)
    if mesh is None:
        stats = STATS_NOT_FOUND
        logging.warning(f"Mesh stats unavailable for {mesh_path}.")
    else:
        stats = {
            'Volume': f"{mesh.volume:.3f}",
            'Surface Area': f"{mesh.area:.3f}",
            'Face Count': str(len(mesh.faces)),
            'Vertex Count': str(len(mesh.vertices))
        }
        logging.info(f"Mesh stats: {stats}")
    return stats


def load_metadata(meta_path):
    try:
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        logging.info(f"Loaded metadata from {meta_path}.")
        return meta
    except Exception as e:
        logging.error(f"Failed to load metadata from {meta_path}: {e}")
        return {}


def app():
    with gr.Blocks(title="YanMesh") as demo:
        gr.Markdown("# YanMesh: 3D Viewer + Metadata Editor")
        with gr.Row():
            with gr.Column():
                mesh_file = gr.File(
                    label="Upload 3D Mesh (.stl, .obj, .ply)",
                    file_types=[".stl", ".obj", ".ply"]
                )
                default_mesh_btn = gr.Button("Use Default Mesh (bunny.obj)")
                mesh_viewer = gr.Plot(label="3D Viewer")
                stats_output = gr.JSON(label="Mesh Stats")
            with gr.Column():
                meta_file = gr.File(label="Upload Metadata (.json)")
                default_meta_btn = gr.Button("Use Default Metadata (bunny.json)")
                meta_json = gr.Textbox(label="Metadata (Read-Only, Compact)", interactive=False, lines=4)

        def on_mesh_upload(file):
            if file is None:
                logging.info("No mesh uploaded.")
                return go.Figure(), STATS_NOT_FOUND
            mesh_path = file.name
            logging.info(f"User uploaded mesh: {mesh_path}")
            fig, mesh = mesh_to_plot(mesh_path)
            stats = load_mesh_stats(mesh_path)
            return fig, stats

        mesh_file.change(
            fn=on_mesh_upload,
            inputs=mesh_file,
            outputs=[mesh_viewer, stats_output]
        )

        def on_default_mesh():
            logging.info("User selected default mesh.")
            fig, mesh = mesh_to_plot(DEFAULT_MESH_PATH)
            stats = load_mesh_stats(DEFAULT_MESH_PATH)
            return fig, stats

        default_mesh_btn.click(
            fn=on_default_mesh,
            inputs=None,
            outputs=[mesh_viewer, stats_output]
        )

        def on_meta_upload(file):
            if file is None:
                logging.info("No metadata uploaded.")
                return ""
            meta = load_metadata(file.name)
            logging.info(f"User uploaded metadata: {file.name}")
            return json.dumps(meta, separators=(",", ":"))

        meta_file.change(
            fn=on_meta_upload,
            inputs=meta_file,
            outputs=meta_json
        )

        def on_default_meta():
            logging.info("User selected default metadata.")
            meta = load_metadata(DEFAULT_META_PATH)
            return json.dumps(meta, separators=(",", ":"))

        default_meta_btn.click(
            fn=on_default_meta,
            inputs=None,
            outputs=meta_json
        )

    return demo


if __name__ == "__main__":
    app().launch()
