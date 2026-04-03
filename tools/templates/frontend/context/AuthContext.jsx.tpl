import { createContext, useContext, useMemo } from "react";

const AuthContext = createContext({
  user: null,
  memberships: [],
  scopedDepartments: [],
});

export function AuthProvider({ children, value }) {
  const contextValue = useMemo(() => ({
    user: value?.user ?? null,
    memberships: value?.memberships ?? [],
    scopedDepartments: value?.scopedDepartments ?? [],
  }), [value]);

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
