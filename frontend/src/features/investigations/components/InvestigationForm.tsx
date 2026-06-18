import { FormEvent, useState } from "react";

export type InvestigationFormValues = {
  title: string;
  summary: string;
  root_cause_hypothesis: string;
  status: string;
};

type InvestigationFormProps = {
  initialValues?: Partial<InvestigationFormValues>;
  isSaving?: boolean;
  submitLabel: string;
  onSubmit: (values: InvestigationFormValues) => void;
};

const defaultValues: InvestigationFormValues = {
  title: "",
  summary: "",
  root_cause_hypothesis: "",
  status: "active",
};

export function InvestigationForm({
  initialValues,
  isSaving = false,
  onSubmit,
  submitLabel,
}: InvestigationFormProps) {
  const [values, setValues] = useState<InvestigationFormValues>({
    ...defaultValues,
    ...initialValues,
  });

  function updateField(field: keyof InvestigationFormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form className="workflow-form" data-testid="investigation-form" onSubmit={handleSubmit}>
      <label>
        Title
        <input
          value={values.title}
          onChange={(event) => updateField("title", event.target.value)}
          required
        />
      </label>
      <label>
        Summary
        <textarea
          value={values.summary}
          onChange={(event) => updateField("summary", event.target.value)}
          rows={4}
        />
      </label>
      <label>
        Root-cause hypothesis
        <textarea
          value={values.root_cause_hypothesis}
          onChange={(event) => updateField("root_cause_hypothesis", event.target.value)}
          rows={4}
        />
      </label>
      <label>
        Status
        <select
          data-testid="investigation-status-select"
          value={values.status}
          onChange={(event) => updateField("status", event.target.value)}
        >
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="waiting_on_data">Waiting on Data</option>
          <option value="resolved">Resolved</option>
        </select>
      </label>
      <button className="secondary-button" data-testid="save-investigation-button" type="submit" disabled={isSaving}>
        {submitLabel}
      </button>
    </form>
  );
}
