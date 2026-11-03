import { Router } from 'express';
import { getPool } from './db.js';

const router = Router();
const VALID_STATUSES = ['pending', 'completed'];

function parseStatusFilter(value) {
  if (!value) return null;
  const normalized = String(value).trim().toLowerCase();
  const map = {
    pending: 'pending',
    incomplete: 'pending',
    not_completed: 'pending',
    completed: 'completed',
    complete: 'completed',
    done: 'completed',
  };
  return map[normalized] || null;
}

function parseDueDate(value) {
  if (value === null || value === undefined || value === '') return { ok: true, value: null };
  if (typeof value !== 'string') return { ok: false };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return { ok: false };
  const d = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return { ok: false };
  return { ok: true, value };
}

function toTask(row) {
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    status: row.status,
    due_date: row.due_date,
    created_at: row.created_at,
    updated_at: row.updated_at,
  };
}

// GET /api/tasks?status=completed|pending
router.get('/', async (req, res) => {
  const status = parseStatusFilter(req.query.status);
  try {
    const pool = getPool();
    let result;
    if (status) {
      result = await pool.query(
        'SELECT * FROM tasks WHERE user_id = $1 AND status = $2 ORDER BY created_at DESC',
        [req.userId, status]
      );
    } else {
      result = await pool.query(
        'SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC',
        [req.userId]
      );
    }
    res.status(200).json({ tasks: result.rows.map(toTask), count: result.rowCount });
  } catch (err) {
    console.error('List tasks error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/tasks
router.post('/', async (req, res) => {
  const { title, description = '', due_date, status = 'pending' } = req.body;

  if (!title || typeof title !== 'string' || !title.trim()) {
    return res.status(400).json({ error: 'Title is required' });
  }
  if (title.trim().length > 255) {
    return res.status(400).json({ error: 'Title must be 255 characters or fewer' });
  }
  if (typeof description !== 'string') {
    return res.status(400).json({ error: 'Description must be a string' });
  }
  if (!VALID_STATUSES.includes(status)) {
    return res.status(400).json({ error: 'Status must be pending or completed' });
  }
  const parsed = parseDueDate(due_date);
  if (!parsed.ok) {
    return res.status(400).json({ error: 'due_date must be YYYY-MM-DD or null' });
  }

  try {
    const pool = getPool();
    const result = await pool.query(
      `INSERT INTO tasks (user_id, title, description, status, due_date)
       VALUES ($1, $2, $3, $4, $5) RETURNING *`,
      [req.userId, title.trim(), description, status, parsed.value]
    );
    res.status(201).json({ message: 'Task created', task: toTask(result.rows[0]) });
  } catch (err) {
    console.error('Create task error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/tasks/:id
router.get('/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: 'Invalid task id' });
  try {
    const pool = getPool();
    const result = await pool.query(
      'SELECT * FROM tasks WHERE id = $1 AND user_id = $2',
      [id, req.userId]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: 'Task not found' });
    res.status(200).json({ task: toTask(result.rows[0]) });
  } catch (err) {
    console.error('Get task error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/tasks/:id
router.put('/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: 'Invalid task id' });

  const { title, description, status, due_date } = req.body;
  if (title === undefined && description === undefined && status === undefined && due_date === undefined) {
    return res.status(400).json({ error: 'At least one field is required' });
  }

  const updates = [];
  const values = [];
  let i = 1;

  if (title !== undefined) {
    if (typeof title !== 'string' || !title.trim()) {
      return res.status(400).json({ error: 'Title must be a non-empty string' });
    }
    if (title.trim().length > 255) {
      return res.status(400).json({ error: 'Title must be 255 characters or fewer' });
    }
    updates.push(`title = $${i++}`);
    values.push(title.trim());
  }
  if (description !== undefined) {
    if (typeof description !== 'string') {
      return res.status(400).json({ error: 'Description must be a string' });
    }
    updates.push(`description = $${i++}`);
    values.push(description);
  }
  if (status !== undefined) {
    if (!VALID_STATUSES.includes(status)) {
      return res.status(400).json({ error: 'Status must be pending or completed' });
    }
    updates.push(`status = $${i++}`);
    values.push(status);
  }
  if (due_date !== undefined) {
    const parsed = parseDueDate(due_date);
    if (!parsed.ok) {
      return res.status(400).json({ error: 'due_date must be YYYY-MM-DD or null' });
    }
    updates.push(`due_date = $${i++}`);
    values.push(parsed.value);
  }

  try {
    const pool = getPool();
    const result = await pool.query(
      `UPDATE tasks SET ${updates.join(', ')}, updated_at = NOW()
       WHERE id = $${i} AND user_id = $${i + 1} RETURNING *`,
      [...values, id, req.userId]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: 'Task not found' });
    res.status(200).json({ message: 'Task updated', task: toTask(result.rows[0]) });
  } catch (err) {
    console.error('Update task error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// DELETE /api/tasks/:id
router.delete('/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: 'Invalid task id' });
  try {
    const pool = getPool();
    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, req.userId]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: 'Task not found' });
    res.status(200).json({ message: 'Task deleted' });
  } catch (err) {
    console.error('Delete task error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
