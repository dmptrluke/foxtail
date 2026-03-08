import rules

is_verifier = rules.is_group_member('verifiers')

rules.add_perm('accounts.verify_user', is_verifier)
