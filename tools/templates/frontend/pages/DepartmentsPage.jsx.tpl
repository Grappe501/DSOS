import { useEffect, useState } from "react";

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    setDepartments([]);
  }, []);

  return (
    <section>
      <h1>${page_title}</h1>
      <p>${slice_summary}</p>
      <div className="card">
        <strong>Starter scaffold</strong>
        <p>Wire department create, list, membership assignment, and scope views here.</p>
        <pre>{JSON.stringify(departments, null, 2)}</pre>
      </div>
    </section>
  );
}
