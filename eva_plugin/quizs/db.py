from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set, row_to_obj, QueryError


class DatabaseConnector:
    def __init__(self):
        self.pg = PGConnector()

    # __QUIZS__ ###############################################################

    QUIZ_TABLES = {'bool': 'boolAnswer', 'date': 'dateAnswer', 'text': 'textAnswer',
                   'cascade': 'cascadeAnswer', 'multi': 'multiAnswer', 'catalog': 'catalogAnswer'}

    def check_quiz_exists(self, quiz_name):
        quiz_id = self.pg.execute_query("SELECT id FROM quiz WHERE name = %s;", params=(quiz_name,))
        return quiz_id

    def get_quizs_count(self):
        count = self.pg.execute_query("SELECT COUNT(id) FROM quiz;")
        return count[0]

    def get_quizs(self, *, limit, offset):
        quizs_data = self.pg.execute_query("SELECT * FROM quiz ORDER BY id limit %s offset %s;",
                                        params=(limit, offset), fetchall=True, as_obj=True)
        return quizs_data

    def get_quiz(self, quiz_id):
        quiz_data = self.pg.execute_query("SELECT * FROM quiz WHERE id = %s;", params=(quiz_id,), as_obj=True)
        if not quiz_data:
            raise QueryError(f'quiz with id={quiz_id} not exists')
        questions_data = self.pg.execute_query("SELECT id, text, description, type, sid FROM question "
                                            "WHERE quiz_id = %s;", params=(quiz_id,), fetchall=True, as_obj=True)
        for q in questions_data:
            q_id = q.pop('id')
            if q['type'] == 'cascade':
                q['childs'] = self.load_cascade(root_id=q_id)

        quiz_data['questions'] = questions_data
        return quiz_data

    def add_quiz(self, *, name, questions):
        if self.check_quiz_exists(quiz_name=name):
            raise QueryError(f'quiz {name} already exists')

        with self.pg.transaction('create_quiz_data') as conn:
            quiz_id = self.pg.execute_query("INSERT INTO quiz (name) values (%s) RETURNING id;",
                                         conn=conn, params=(name,))
            if not isinstance(questions, list):
                return quiz_id
            for sid, q in enumerate(questions, 1):
                if q['type'] == 'cascade':
                    self.save_cascade(question=q, quiz_id=quiz_id, sid=sid, conn=conn)
                else:
                    self.pg.execute_query(
                        "INSERT INTO question (text, type, is_sign, description, label, sid, quiz_id, catalog_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                        conn=conn, params=(q['text'], q['type'], q.get('is_sign', False), q.get('description'),
                                           q.get('label'), sid, quiz_id, q.get('catalog_id')))
        return quiz_id

    def save_cascade(self, *, parent_id=None, quiz_id=None, sid=None, question, conn):
        saved_id = self.pg.execute_query(
            "INSERT INTO question (text, type, is_sign, description, label, sid, quiz_id, parent_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            conn=conn, params=(question['text'], question['type'], question.get('is_sign', False),
                               question.get('description'), question.get('label'), sid, quiz_id, parent_id))
        childs = question.get('childs')
        if not childs:
            return

        for child in childs:
            if child['type'] == 'cascade':
                self.save_cascade(parent_id=saved_id, question=child, conn=conn)
            else:
                self.pg.execute_query(
                    "INSERT INTO question (text, type, is_sign, description, label, parent_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                    conn=conn, params=(child['text'], child['type'], child.get('is_sign', False),
                                       child.get('description'), child.get('label'), saved_id))

    def load_cascade(self, root_id):
        childs = self.pg.execute_query("SELECT id, type, text, sid FROM question WHERE parent_id = %s ORDER BY id;",
                                    params=(root_id,), fetchall=True, as_obj=True)
        for child in childs:
            c_id = child.pop('id')
            if child['type'] == 'cascade':
                child['childs'] = self.load_cascade(root_id=c_id)
        return childs

    def update_quiz(self, *, quiz_id, name, questions=None):
        with self.pg.transaction('update_quiz_data') as conn:
            if name:
                self.pg.execute_query("UPDATE quiz SET name = %s WHERE id = %s;",
                                   conn=conn, params=(name, quiz_id), with_fetch=False)
            if not isinstance(questions, list):
                return quiz_id

            self.pg.execute_query("DELETE FROM question WHERE quiz_id = %s;",
                               conn=conn, params=(quiz_id,), with_fetch=False)
            for sid, q in enumerate(questions, 1):
                if q['type'] == 'cascade':
                    self.save_cascade(question=q, quiz_id=quiz_id, sid=sid, conn=conn)
                else:
                    self.pg.execute_query(
                        "INSERT INTO question (text, type, is_sign, description, label, sid, quiz_id, catalog_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                        conn=conn, params=(q['text'], q['type'], q.get('is_sign', False),
                                           q.get('description'), q.get('label'), sid, quiz_id, q['catalog_id']))
        return quiz_id

    def get_quiz_questions(self, quiz_ids):
        quizs = dict()
        questions_data = self.pg.execute_query(
            "select question.id as id, sid, text, description, type, is_sign, catalog_id, "
            "label, quiz.name as quiz_name, quiz.id as qid from question inner join quiz on quiz_id=quiz.id "
            "where question.quiz_id in %s order by sid;", params=(tuple(quiz_ids),), fetchall=True,
            as_obj=True)

        for question in questions_data:
            quiz_name = question['quiz_name']
            quiz_id = question['qid']

            if question['type'] == 'cascade':
                question['childs'] = self.load_cascade(root_id=question.pop('id'))

            if question.qid in quizs:
                quizs[quiz_id]['questions'].append(question)
            else:
                quizs[quiz_id] = {'id': quiz_id, 'name': quiz_name, 'questions': [question]}
        return list(quizs.values())

    def get_filled_quizs_count(self, quiz_id):
        count = self.pg.execute_query("SELECT COUNT(id) FROM filled_quiz WHERE quiz_id = %s;", params=(quiz_id,))
        return count[0]

    def get_filled_quiz(self, *, offset=0, limit=1, quiz_id=None, current=False):
        # Get current quiz from filled_quiz table
        if quiz_id and current:
            f_quizs = self.pg.execute_query(
                "SELECT * FROM filled_quiz WHERE id = %s limit %s offset %s;",
                params=(quiz_id, limit, offset), fetchall=True, as_obj=True)
            self.logger.debug("SELECT * FROM filled_quiz WHERE id = %s limit %s offset %s;" % (quiz_id, limit, offset))
            self.logger.debug(f_quizs)

            answer_id = quiz_id
            quiz_id = f_quizs[0].quiz_id if f_quizs else None
            quiz_name = self.pg.execute_query("SELECT name FROM quiz WHERE id = %s;", params=(quiz_id,), as_obj=True)
            self.logger.debug("SELECT name FROM quiz WHERE id = %s;" % quiz_id)
            self.logger.debug(quiz_name)

        # Get filled quizs for current base quiz
        elif quiz_id:
            f_quizs = self.pg.execute_query("SELECT * FROM filled_quiz WHERE quiz_id = %s order by id limit %s offset %s;",
                                         params=(quiz_id, limit, offset), fetchall=True, as_obj=True)
            quiz_name = self.pg.execute_query('SELECT name FROM quiz WHERE id = %s;',
                                           params=(quiz_id,), as_obj=True)
        # If not quiz_id get statistic by quiz name, filler and last fill date
        # TODO: Maybe better to move this section in separate handler
        else:
            f_quizs = self.pg.execute_query("select distinct on (quiz_id) quiz_id, fill_date, filler, "
                                         "quiz.name as name from filled_quiz inner join quiz on quiz.id=quiz_id "
                                         "order by quiz_id, fill_date desc;", fetchall=True, as_obj=True)
            for quiz in f_quizs:
                quiz['fill_date'] = str(quiz.fill_date)
            return f_quizs

        _questions = self.pg.execute_query("SELECT id, sid, type, text, is_sign, label FROM question "
                                        "WHERE quiz_id = %s ORDER BY sid;", as_obj=True,
                                        params=(quiz_id,), fetchall=True)
        self.logger.debug(
            "SELECT id, sid, type, text, is_sign, label FROM question WHERE quiz_id = %s ORDER BY sid;" % quiz_id)

        for quiz in f_quizs:
            questions = deepcopy(_questions)
            answers = self.pg.execute_query(
                'select filled_quiz.id as filled_quiz_id, question.type, question.sid as sid, '
                'coalesce(textanswer.value, cascadeanswer.value, multianswer.value::text, '
                'cataloganswer.value, dateanswer.value::text) as value, '
                'coalesce (textanswer.description, cascadeanswer.description, multianswer.description, '
                'cataloganswer.description, dateanswer.description) as description from filled_quiz '
                'join question on question.quiz_id=filled_quiz.quiz_id '
                'left join textanswer on textanswer.id=filled_quiz.id and textanswer.sid=question.sid '
                'left join cascadeanswer on cascadeanswer.id=filled_quiz.id and cascadeanswer.sid=question.sid '
                'left join multianswer on multianswer.id=filled_quiz.id and multianswer.sid=question.sid '
                'left join cataloganswer on cataloganswer.id=filled_quiz.id and cataloganswer.sid=question.sid '
                'left join dateanswer on dateanswer.id=filled_quiz.id and dateanswer.sid=question.sid '
                'where filled_quiz.id = %s order by question.sid;',
                params=(quiz.id,), fetchall=True, as_obj=True
            )
            self.logger.debug('select filled_quiz.id as filled_quiz_id, question.type, question.sid as sid, '
                              'coalesce(textanswer.value, cascadeanswer.value, multianswer.value::text, '
                              'cataloganswer.value, dateanswer.value::text) as value, '
                              'coalesce (textanswer.description, cascadeanswer.description, multianswer.description, '
                              'cataloganswer.description, dateanswer.description) as description from filled_quiz '
                              'join question on question.quiz_id=filled_quiz.quiz_id '
                              'left join textanswer on textanswer.id=filled_quiz.id and textanswer.sid=question.sid '
                              'left join cascadeanswer on cascadeanswer.id=filled_quiz.id and cascadeanswer.sid=question.sid '
                              'left join multianswer on multianswer.id=filled_quiz.id and multianswer.sid=question.sid '
                              'left join cataloganswer on cataloganswer.id=filled_quiz.id and cataloganswer.sid=question.sid '
                              'left join dateanswer on dateanswer.id=filled_quiz.id and dateanswer.sid=question.sid '
                              'where filled_quiz.id = %s order by question.sid;' % quiz.id)

            for q, a in zip(questions, answers):
                q['answer'] = a
            quiz['questions'] = questions
            quiz['name'] = quiz_name.name
            quiz['fill_date'] = str(quiz.fill_date)
        return f_quizs

    def save_filled_quiz(self, *, user_id, quiz_id, questions):
        with self.pg.transaction('save_quiz') as conn:
            user = self.pg.execute_query('SELECT name FROM "user" WHERE id = %s;', conn=conn,
                                      params=(user_id,), as_obj=True)
            quiz = self.pg.execute_query("INSERT INTO filled_quiz (filler, quiz_id) VALUES (%s, %s) RETURNING id;",
                                      conn=conn, params=(user.name, quiz_id,), as_obj=True)

            for sid, q in enumerate(questions, 1):
                answer = q.pop('answer', None)
                if not answer:
                    continue
                table = self.QUIZ_TABLES.get(q['type'])
                if not table:
                    raise QueryError(f'answer with type {q["type"]} is not exists')
                query = "INSERT INTO %s (id, sid, value, description) VALUES (%%s, %%s, %%s, %%s);" % table
                self.pg.execute_query(query, conn=conn, with_fetch=False,
                                   params=(quiz.id, sid, answer['value'], answer.get('description')))
        return quiz_id

    def delete_quiz(self, quiz_id):
        self.pg.execute_query("DELETE FROM quiz WHERE id = %s;",
                           params=(quiz_id,), with_commit=True, with_fetch=False)
        return


db = DatabaseConnector()
