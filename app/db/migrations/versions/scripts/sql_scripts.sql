select * from public.permissions

INSERT INTO PUBLIC.ROLES(NAME)
VALUES
('ADMIN'),
('USER'),
('MODERATOR')
ON CONFLICT (name) DO NOTHING;


INSERT INTO public.role_permission_association(
	role_id, permission_id)
	VALUES
	(2, 1),
	(2, 3),
	(2, 4),
	(2, 5)
ON CONFLICT DO NOTHING;


INSERT INTO public.role_permission_association(role_id, permission_id)
SELECT 1 AS role_id, id AS permission_id
FROM public.permissions
ON CONFLICT (role_id, permission_id) DO NOTHING;


