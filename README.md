✦ To-Do App
A lightweight, persistent To-Do web application built with Python and Flask. Features a sleek dark UI accessible from any browser, with full Docker support for easy deployment.

📸 Features

✅ Add tasks with title, priority (high / medium / low), and due date
🔁 Toggle tasks between pending and done
✏️ Edit tasks via a modal popup
🗑️ Delete tasks with a confirmation prompt
🔍 Filter by All / Pending / Done / High Priority / Overdue
⚠️ Overdue tasks are automatically highlighted in red
💾 Tasks are persisted to todo_data.json — survive restarts
🌐 Accessible from your browser at http://localhost:5000


📁 Project Structure
todo-app/
    app.py              # Flask web application            
    requirements.txt    # Python dependencies
    Dockerfile          # Docker container config
    README.md
