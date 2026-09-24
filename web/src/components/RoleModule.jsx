import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api";

const DEMO = {
  Attendance: [
    ["23 Sep 2026", "Present", "Daily", "Present"],
    ["22 Sep 2026", "Present", "Daily", "Present"],
    ["21 Sep 2026", "Absent", "Daily", "Absent"],
  ],
  Homework: [
    ["Algebra Exercise – Chapter 4", "MAT-104", "Mathematics", "Pending"],
    ["Chapter 6 Worksheet", "SCI-206", "Science", "Submitted"],
  ],
  Results: [
    ["Mathematics", "92/100", "Semester I", "A+"],
    ["Science", "88/100", "Semester I", "A"],
  ],
  Fees: [
    ["Term I Fee", "₹25,000", "Tuition", "Paid"],
    ["Transport Fee", "₹6,000", "Transport", "Paid"],
  ],
  Transport: [["Route A1", "GAINT BUS 12", "Pickup 08:00", "Active"]],
  "My Children": [["Demo Student", "STU-1001", "Class 10-A", "Active"]],
  "My Classes": [
    ["Class 10-A Mathematics", "10A-MAT", "Period 2", "Today"],
    ["Class 9-B Mathematics", "9B-MAT", "Period 5", "Today"],
  ],
  "My Students": [
    ["Aarav Sharma", "STU-1001", "10-A", "Active"],
    ["Diya Reddy", "STU-1002", "10-A", "Active"],
  ],
  Payments: [["PAY-2026-901", "₹12,500", "UPI", "Success"]],
  Receipts: [["RCPT-2026-901", "₹12,500", "Tuition", "Issued"]],
  Refunds: [["RF-2026-04", "₹2,000", "Duplicate Payment", "Pending"]],
  Staff: [
    ["Ananya Rao", "EMP-101", "Teacher", "Active"],
    ["Rahul Verma", "EMP-102", "Administration", "Active"],
  ],
  Visitors: [["Ramesh Kumar", "VIS-902", "Parent Meeting", "Checked In"]],
  Inventory: [["Projectors", "INV-PRJ", "AV Equipment", "42 Available"]],
  Assets: [["Computer Lab", "AST-LAB-01", "IT", "Operational"]],
  Compliance: [["Fee Reconciliation Review", "CMP-09", "Finance", "In Review"]],
  "Exception Reports": [["Unusual Fee Adjustment", "EX-14", "Finance", "Open"]],
  Evidence: [["September Audit Evidence", "EVD-SEP", "Audit", "Available"]],
};

function demoRows(title) {
  return (DEMO[title] || []).map((item, index) => ({
    id: `demo-${index}`,
    name: item[0],
    code: item[1],
    category: item[2],
    status: item[3],
    notes: "",
    isDemo: true,
  }));
}

function csvEscape(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

export default function RoleModule({ title, user }) {
  const [access, setAccess] = useState(null);
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({
    name: "",
    code: "",
    category: "General",
    status: "Active",
    notes: "",
  });
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const permissions = useMemo(
    () => new Set(access?.permissions || []),
    [access]
  );

  const canCreate = permissions.has("create");
  const canUpdate = permissions.has("update");
  const canDelete = permissions.has("delete");
  const canExport = permissions.has("export");
  const canPay = permissions.has("pay");
  const canMessage = permissions.has("message");
  const canApprove = permissions.has("approve");
  const canCreateGrievance = permissions.has("create_grievance");
  const canRequestLeave = permissions.has("request_leave");
  const canManageUsers = permissions.has("manage_users");

  const resetForm = () => {
    setForm({
      name: "",
      code: "",
      category: "General",
      status: "Active",
      notes: "",
    });
    setEditingId(null);
  };

  async function fetchRows(accessData) {
    const perms = new Set(accessData?.permissions || []);
    const mutatingPage = perms.has("create") || perms.has("update") || perms.has("delete");

    if (!mutatingPage && DEMO[title]) {
      setRows(demoRows(title));
      return;
    }

    const response = await api.get("/api/v1/records", {
      params: { module: title },
    });
    setRows(response.data);
  }

  async function initialize() {
    try {
      setLoading(true);
      setError("");
      setSuccess("");
      setAccess(null);
      setRows([]);
      resetForm();

      const accessResponse = await api.get(
        `/api/v1/module-access/${encodeURIComponent(title)}`
      );
      setAccess(accessResponse.data);
      await fetchRows(accessResponse.data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err.message ||
          "Unable to load module."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    initialize();
  }, [title, user.role]);

  function setField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
    setError("");
    setSuccess("");
  }

  async function handleSave() {
    const name = form.name.trim();

    if (!name) {
      setError(`Please enter a ${title} record name first.`);
      setSuccess("");
      return;
    }

    const payload = {
      module: title,
      name,
      code: form.code.trim(),
      category: form.category.trim() || "General",
      status: form.status.trim() || "Active",
      notes: form.notes.trim(),
    };

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      if (editingId !== null) {
        if (!canUpdate) {
          throw new Error("You do not have permission to update this record.");
        }
        await api.put(`/api/v1/records/${editingId}`, payload);
        setSuccess(`${title} record updated successfully.`);
      } else {
        if (!canCreate) {
          throw new Error("You do not have permission to create records in this module.");
        }
        await api.post("/api/v1/records", payload);
        setSuccess(`${title} record added successfully.`);
      }

      resetForm();
      const response = await api.get("/api/v1/records", {
        params: { module: title },
      });
      setRows(response.data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err.message ||
          "Unable to save record."
      );
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(record) {
    if (!canUpdate || record.isDemo) {
      setError(
        record.isDemo
          ? "Demo rows are read-only."
          : "You do not have permission to update this record."
      );
      return;
    }

    setEditingId(record.id);
    setForm({
      name: record.name || "",
      code: record.code || "",
      category: record.category || "General",
      status: record.status || "Active",
      notes: record.notes || "",
    });
    setError("");
    setSuccess(`Editing "${record.name}".`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(record) {
    if (!canDelete || record.isDemo) {
      setError(
        record.isDemo
          ? "Demo rows cannot be deleted."
          : "You do not have permission to delete this record."
      );
      return;
    }

    if (!window.confirm(`Delete "${record.name}"?`)) return;

    try {
      setError("");
      setSuccess("");
      await api.delete(`/api/v1/records/${record.id}`);
      setRows((current) => current.filter((item) => item.id !== record.id));
      setSuccess("Record deleted successfully.");
      if (editingId === record.id) resetForm();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err.message ||
          "Unable to delete record."
      );
    }
  }

  function handleExport() {
    if (!canExport) return;

    const headers = ["Name / Item", "Code / Value", "Category", "Status", "Notes"];
    const body = rows.map((row) => [
      row.name,
      row.code,
      row.category,
      row.status,
      row.notes || "",
    ]);
    const csv = [headers, ...body]
      .map((line) => line.map(csvEscape).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replaceAll(/[^a-zA-Z0-9]+/g, "_")}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    setSuccess("CSV export generated.");
  }

  async function runModuleAction(action, label) {
    try {
      setError("");
      setSuccess("");

      let details = `${label} requested from ${title}.`;
      if (["message", "create_grievance", "request_leave"].includes(action)) {
        const entered = window.prompt(`${label}: enter details`);
        if (entered === null) return;
        if (!entered.trim()) {
          setError("Please enter details.");
          return;
        }
        details = entered.trim();
      }

      const { data } = await api.post(
        `/api/v1/module-actions/${action}`,
        { page: title, details }
      );
      setSuccess(data.message || `${label} completed.`);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err.message ||
          `${label} failed.`
      );
    }
  }

  if (!access && error) return <div className="error">{error}</div>;
  if (!access) return <div>Loading module...</div>;

  return (
    <div>
      <div className="page-title">
        <div>
          <h1>{title}</h1>
          <p>
            {access.read_only
              ? `Read-only records for ${user.role}`
              : `${user.role} workspace`}
          </p>
        </div>

        <div className="page-actions">
          {canExport && (
            <button type="button" className="secondary" onClick={handleExport}>
              Export
            </button>
          )}
          {canPay && (
            <button
              type="button"
              className="primary"
              onClick={() => runModuleAction("pay", "Payment")}
            >
              Pay / Payment Details
            </button>
          )}
          {canMessage && (
            <button
              type="button"
              className="primary"
              onClick={() => runModuleAction("message", "New Message")}
            >
              New Message
            </button>
          )}
          {canApprove && (
            <button
              type="button"
              className="primary"
              onClick={() => runModuleAction("approve", "Approval")}
            >
              Approvals
            </button>
          )}
          {canCreateGrievance && (
            <button
              type="button"
              className="primary"
              onClick={() => runModuleAction("create_grievance", "Raise Grievance")}
            >
              Raise Grievance
            </button>
          )}
          {canRequestLeave && (
            <button
              type="button"
              className="primary"
              onClick={() => runModuleAction("request_leave", "Request Leave")}
            >
              Request Leave
            </button>
          )}
          {canManageUsers && (
            <button
              type="button"
              className="primary"
              onClick={() => runModuleAction("manage_users", "User Management")}
            >
              Manage Users
            </button>
          )}
        </div>
      </div>

      <section className="panel">
        {(canCreate || (canUpdate && editingId !== null)) ? (
          <div className="record-form">
            <div className="inline-form">
              <input
                type="text"
                value={form.name}
                placeholder={`Enter ${title} record name`}
                onChange={(e) => setField("name", e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleSave();
                  }
                }}
              />
              <input
                type="text"
                value={form.code}
                placeholder="Code / Value"
                onChange={(e) => setField("code", e.target.value)}
              />
              <input
                type="text"
                value={form.category}
                placeholder="Category"
                onChange={(e) => setField("category", e.target.value)}
              />
              <select
                value={form.status}
                onChange={(e) => setField("status", e.target.value)}
              >
                <option>Active</option>
                <option>Pending</option>
                <option>Approved</option>
                <option>Completed</option>
                <option>Inactive</option>
              </select>
              <button
                type="button"
                className="primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? "Saving..." : editingId !== null ? "Update" : "Add"}
              </button>
              {editingId !== null && (
                <button type="button" className="secondary" onClick={resetForm}>
                  Cancel
                </button>
              )}
            </div>
            <textarea
              value={form.notes}
              placeholder="Notes (optional)"
              onChange={(e) => setField("notes", e.target.value)}
              rows={3}
            />
          </div>
        ) : (
          <div className="readonly-note">
            No record create/edit controls are available for <b>{user.role}</b> on this page.
          </div>
        )}

        {error && <div className="error">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {loading ? (
          <div className="readonly-note">Loading records...</div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Name / Item</th>
                  <th>Code / Value</th>
                  <th>Category</th>
                  <th>Status</th>
                  {(canUpdate || canDelete) && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td
                      colSpan={canUpdate || canDelete ? 5 : 4}
                      className="empty-cell"
                    >
                      No records available.
                    </td>
                  </tr>
                ) : (
                  rows.map((record, index) => (
                    <tr key={record.id ?? index}>
                      <td>{record.name}</td>
                      <td>{record.code || "—"}</td>
                      <td>{record.category || "—"}</td>
                      <td>{record.status || "—"}</td>
                      {(canUpdate || canDelete) && (
                        <td>
                          {canUpdate && !record.isDemo && (
                            <button
                              type="button"
                              className="table-action"
                              onClick={() => handleEdit(record)}
                            >
                              Edit
                            </button>
                          )}
                          {canDelete && !record.isDemo && (
                            <button
                              type="button"
                              className="table-action danger"
                              onClick={() => handleDelete(record)}
                            >
                              Delete
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
