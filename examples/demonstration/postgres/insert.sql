DELETE FROM public."B";

DELETE FROM public."C";

INSERT INTO public."B" (c, d) VALUES (%(id)s, %(c)s); INSERT INTO public."C" (e, f) VALUES (%(id)s, %(d)s);
